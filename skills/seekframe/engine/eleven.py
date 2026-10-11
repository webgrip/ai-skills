#!/usr/bin/env python3
"""Careful ElevenLabs voice-over for a seekframe project, one subtitle line at a time.

Nothing is spent without --go. Every spending run is capped (--max-credits, default 300) and refused
when it would pass the credits left in the plan. The first error stops the run; nothing is retried.
Lines are cached by voice, model, text and settings, so a line is never paid for twice.

The project is SEEKFRAME_PROJECT or --project (default: the current directory). Rendered subtitles are
read from <project>/out/<group>/<id>.srt; voice files live in <project>/voice.

Key: ELEVENLABS_API_KEY, else the keyring entry ELEVENLABS_KEYRING (default elevenlabs-voiceover,
user ELEVENLABS_API_KEY), else ~/.config/elevenlabs/api_key (mode 600). The key is never printed.

  eleven.py status                              plan, credits used and left (free)
  eleven.py models                              text-to-speech models and their credit multiplier (free)
  eleven.py voices [--search calm] [--lang nl]  voices on the account (free)
  eleven.py preview VOICE_ID                    the voice's own preview sample (free)
  eleven.py plan [--tier N] [--video ID]        what each tier would cost (free)
  eleven.py gen --tier 0 --model cheapest       dry run of the test hooks, one per voice
  eleven.py gen --tier 0 --model cheapest --go  spend it
  eleven.py place [--model ID]                  copy complete videos' lines to voice/ID-NN.mp3 for voice.sh
  eleven.py srt ID --cues C --timing T --out F  word-timed subtitles after a voice render

Tiers, most certain first: 0 shortest opening hook per voice, 1 other hooks, 2 closing lines, 3 the rest.
"""
import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT = Path(os.environ.get('SEEKFRAME_PROJECT', '.')).resolve()
OUT = PROJECT / 'out'
VOICE = PROJECT / 'voice'
LINES = VOICE / 'lines'
LEDGER = VOICE / 'ledger.jsonl'
CONF = VOICE / 'voices.json'


def use_project(path):
    global PROJECT, OUT, VOICE, LINES, LEDGER, CONF
    PROJECT = Path(path).resolve()
    OUT, VOICE = PROJECT / 'out', PROJECT / 'voice'
    LINES, LEDGER, CONF = VOICE / 'lines', VOICE / 'ledger.jsonl', VOICE / 'voices.json'
BASE = os.environ.get('ELEVENLABS_BASE_URL', 'https://api.elevenlabs.io').rstrip('/')
DEFAULT_CONF = {
    'about': 'One voice_id per output group folder (eleven.py voices); a video id under "videos" overrides its group. '
             'Settings apply to every line; keep them fixed once you start, because changing them changes the cache key.',
    'groups': {},
    'videos': {},
    'languages': {},
    'settings': {'stability': 0.66, 'similarity_boost': 0.78, 'style': 0.1, 'use_speaker_boost': True, 'speed': 1.0},
    'seed': 1,
    'output_format': 'mp3_44100_128',
}


KEYFILE = Path.home() / '.config/elevenlabs/api_key'
_KEY = None


KEYRING = os.environ.get('ELEVENLABS_KEYRING', 'elevenlabs-voiceover')


def key():
    global _KEY
    if _KEY:
        return _KEY
    k = os.environ.get('ELEVENLABS_API_KEY', '').strip()
    if not k:
        import subprocess
        for cmd in ([str(Path.home() / '.local/bin/keyring'), 'get', KEYRING, 'ELEVENLABS_API_KEY'],
                    ['keyring', 'get', KEYRING, 'ELEVENLABS_API_KEY'],
                    ['secret-tool', 'lookup', 'service', KEYRING]):
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
                continue
            k = r.stdout.strip() if r.returncode == 0 else ''
            if k:
                break
    if not k and KEYFILE.exists():
        if KEYFILE.stat().st_mode & 0o077:
            sys.exit(f'{KEYFILE} is readable by others. Run: chmod 600 {KEYFILE}')
        k = KEYFILE.read_text().strip()
    if not k:
        sys.exit(f'No ElevenLabs key found. Export ELEVENLABS_API_KEY from your secrets manager, or cache it once with:\n'
                 f'  keyring set {KEYRING} ELEVENLABS_API_KEY')
    _KEY = k
    return k


def api(method, path, body=None, raw=False, soft=()):
    req = urllib.request.Request(BASE + path, method=method, headers={'xi-api-key': key(), 'Accept': 'application/json'})
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, data=data, timeout=120) as r:
            payload = r.read()
            return (payload, dict(r.headers)) if raw else json.loads(payload)
    except urllib.error.HTTPError as e:
        if e.code in soft:
            return None
        detail = e.read().decode(errors='replace')[:600]
        sys.exit(f'ElevenLabs answered {e.code} for {method} {path}: {detail}\nStopped. Nothing was retried.')
    except urllib.error.URLError as e:
        sys.exit(f'Could not reach ElevenLabs ({e.reason}). Stopped.')


def subscription():
    s = api('GET', '/v1/user/subscription')
    left = int(s['character_limit']) - int(s['character_count'])
    return s, left


def tts_models():
    got = api('GET', '/v1/models', soft=(401, 403))
    if got is None:
        print('Note: this key may not read the model list. Assuming full price (x1) per character; pass --model <id>.')
        return []
    ms = [m for m in got if m.get('can_do_text_to_speech')]
    for m in ms:
        r = m.get('model_rates') or {}
        m['_mult'] = float(r.get('character_cost_multiplier', m.get('token_cost_factor', 1.0)) or 1.0) * float(r.get('cost_discount_multiplier', 1.0) or 1.0)
    return ms


def speaks(m, langs):
    have = {l.get('language_id') for l in (m.get('languages') or [])}
    return not have or set(langs) <= have


def pick_model(name, ms, langs=('en',)):
    if not ms:
        if name == 'cheapest':
            sys.exit('Without the model list I cannot tell which model is cheapest. Pass --model, for example --model eleven_flash_v2_5.')
        return {'model_id': name, '_mult': 1.0}
    if name == 'cheapest':
        ok = [m for m in ms if not m.get('requires_alpha_access') and speaks(m, langs)]
        if not ok:
            sys.exit(f"No model speaks {', '.join(sorted(langs))}.")
        return min(ok, key=lambda m: (m['_mult'], m['model_id']))
    for m in ms:
        if m['model_id'] == name:
            if not speaks(m, langs):
                sys.exit(f"{name} does not speak {', '.join(sorted(set(langs) - {l.get('language_id') for l in m['languages']}))}. Pick another with: python3 eleven.py models")
            return m
    sys.exit(f'Unknown model {name}. Run: python3 eleven.py models')


def parse_srt(p):
    blocks = re.split(r'\n\s*\n', p.read_text(encoding='utf-8').strip())
    out = []
    for b in blocks:
        rows = b.strip().splitlines()
        if len(rows) >= 3:
            out.append(' '.join(rows[2:]).strip())
    return out


def conf():
    VOICE.mkdir(parents=True, exist_ok=True)
    if not CONF.exists():
        CONF.write_text(json.dumps(DEFAULT_CONF, indent=2) + '\n')
    return json.loads(CONF.read_text())


def inventory(c):
    """One entry per (voice, text): which videos and line numbers use it, and its tier."""
    items = {}
    for folder in sorted(d for d in OUT.glob('*') if d.is_dir()):
        group = folder.name
        for srt in sorted(folder.glob('*.srt')):
            vid = srt.stem
            if vid.endswith('-voice'):
                continue
            lines = parse_srt(srt)
            voice = (c.get('videos') or {}).get(vid) or (c.get('groups') or {}).get(group)
            lang = (c.get('languages') or {}).get(vid, 'en')
            for i, text in enumerate(lines):
                tier = 1 if i == 0 else 2 if i == len(lines) - 1 else 3
                k = (voice, text, lang)
                it = items.setdefault(k, {'voice': voice, 'text': text, 'lang': lang, 'uses': [], 'tier': tier, 'group': group})
                it['uses'].append((vid, i + 1))
                it['tier'] = min(it['tier'], tier)
    lst = sorted(items.values(), key=lambda x: (x['tier'], -len(x['uses']), len(x['text'])))
    for voice in {x['voice'] for x in lst if x['voice']}:
        hooks = [x for x in lst if x['tier'] == 1 and x['voice'] == voice]
        if hooks:
            min(hooks, key=lambda x: len(x['text']))['tier'] = 0
    return sorted(lst, key=lambda x: (x['tier'], -len(x['uses']), len(x['text'])))


def cache_key(it, model_id, c):
    blob = json.dumps([it['voice'], model_id, it['text'], it['lang'], c['settings'], c.get('seed'), c.get('output_format'), False], sort_keys=True)
    return hashlib.sha1(blob.encode()).hexdigest()[:16]


def have(k):
    return (LINES / f'{k}.mp3').exists() and (LINES / f'{k}.json').exists()


def cmd_status(a):
    s, left = subscription()
    ext = s.get('max_credit_limit_extension')
    print(f"Plan: {s.get('tier')} ({s.get('status')})")
    print(f"Credits: {s['character_count']:,} used of {s['character_limit']:,} · {left:,} left")
    if s.get('next_character_count_reset_unix'):
        print('Resets:', time.strftime('%Y-%m-%d %H:%M', time.localtime(s['next_character_count_reset_unix'])))
    if ext not in (0, '0', None):
        print(f"Note: overage billing is possible on this account (extension: {ext}). This tool never goes past {left:,}.")
    spent = sum(json.loads(l).get('credits_est', 0) for l in LEDGER.read_text().splitlines()) if LEDGER.exists() else 0
    print(f'Spent through this tool so far (estimated): {spent:,.0f} credits')


def cmd_models(a):
    for m in sorted(tts_models(), key=lambda m: m['_mult']):
        langs = len(m.get('languages') or [])
        flag = '  (alpha access)' if m.get('requires_alpha_access') else ''
        print(f"{m['model_id']:<28} ×{m['_mult']:<5g} max {m.get('maximum_text_length_per_request', '?')} chars · {langs} languages · {m.get('name', '')}{flag}")


def cmd_voices(a):
    q = f'?page_size=100' + (f'&search={urllib.parse.quote(a.search)}' if a.search else '')
    data = api('GET', '/v2/voices' + q)
    for v in data.get('voices', []):
        lab = v.get('labels') or {}
        if a.lang and a.lang not in (lab.get('language', '') + ' ' + lab.get('accent', '')).lower():
            continue
        desc = ', '.join(x for x in [lab.get('gender'), lab.get('age'), lab.get('accent'), lab.get('language'), lab.get('descriptive') or lab.get('description'), lab.get('use_case')] if x)
        print(f"{v['voice_id']}  {v.get('name', ''):<28} {desc}")


def cmd_preview(a):
    v = api('GET', f'/v1/voices/{a.voice_id}')
    url = v.get('preview_url')
    if not url:
        sys.exit('This voice has no preview sample.')
    out = VOICE / 'previews'
    out.mkdir(parents=True, exist_ok=True)
    dst = out / f"{v.get('name', a.voice_id).replace(' ', '_')}-{a.voice_id[:6]}.mp3"
    with urllib.request.urlopen(url, timeout=60) as r:
        dst.write_bytes(r.read())
    print('Saved the free preview to', dst)


def selection(a, c):
    inv = inventory(c)
    sel = [x for x in inv if (a.tier is None or x['tier'] <= a.tier)]
    if a.video:
        sel = [x for x in sel if any(u[0] == a.video for u in x['uses'])] if a.tier is not None else [x for x in inv if any(u[0] == a.video for u in x['uses'])]
    return inv, sel


def cmd_plan(a):
    c = conf()
    inv, sel = selection(a, c)
    names = ['test: the shortest hook per voice', 'opening hooks', 'closing lines', 'everything else']
    ms = None
    try:
        ms = tts_models()
    except SystemExit:
        ms = None
    for t in range(4):
        part = [x for x in sel if x['tier'] == t]
        if not part:
            continue
        chars = sum(len(x['text']) for x in part)
        uses = sum(len(x['uses']) for x in part)
        print(f'\nTier {t} · {names[t]} · {len(part)} lines covering {uses} spots · {chars:,} characters')
        if ms:
            cheap = pick_model('cheapest', ms, {x['lang'] for x in part})
            print(f"  ≈ {chars * cheap['_mult']:,.0f} credits on {cheap['model_id']} (cheapest) · ≈ {chars:,} credits at ×1")
        for x in part[: (12 if a.tier is None or t < a.tier else 60)]:
            v = (x['voice'] or 'NO VOICE SET')[:10]
            where = ', '.join(f'{u[0]}#{u[1]}' for u in x['uses'][:3]) + (f' +{len(x["uses"]) - 3}' if len(x['uses']) > 3 else '')
            print(f"  {len(x['text']):>4}  {v:<12} {x['text'][:70]:<72} {where}")
        if a.tier is None and len(part) > 12:
            print(f'  … {len(part) - 12} more')
    missing = sorted({x['group'] for x in sel if not x['voice']})
    if missing:
        print(f"\nNo voice set yet for: {', '.join(missing)}. Edit {CONF}")


def made_free(k):
    """Audio made on the free plan is for non-commercial use only, so a paid plan makes it again."""
    return json.loads((LINES / f'{k}.json').read_text()).get('plan', 'free') == 'free'


def listen_copy(k, x, c):
    """A readable copy for listening: voice/listen/<voice name>-<video>-<line>.mp3."""
    LISTEN = VOICE / 'listen'
    LISTEN.mkdir(parents=True, exist_ok=True)
    name = (c.get('names') or {}).get(x['voice'], x['voice'][:6]).split(' ')[0]
    vid, line = x['uses'][0]
    (LISTEN / f'{name}-{vid}-{line:02d}.mp3').write_bytes((LINES / f'{k}.mp3').read_bytes())


def cmd_gen(a):
    c = conf()
    inv, sel = selection(a, c)
    if not sel:
        sys.exit('Nothing selected.')
    no_voice = [x for x in sel if not x['voice']]
    if no_voice:
        sys.exit(f"{len(no_voice)} selected lines have no voice yet ({', '.join(sorted({x['group'] for x in no_voice}))}). Set them in {CONF}.")
    ms = tts_models()
    model = pick_model(a.model, ms, {x['lang'] for x in sel})
    s, left = subscription()
    paid = s.get('tier') != 'free'
    todo = [x for x in sel if not have(cache_key(x, model['model_id'], c)) or (paid and made_free(cache_key(x, model['model_id'], c)))]
    if not paid:
        names = c.get('names') or {}
        library = {v for v in {x['voice'] for x in todo} if api('GET', f'/v1/voices/{v}').get('category') != 'premade'}
        held = [x for x in todo if x['voice'] in library]
        if held:
            print(f"Skipping {len(held)} lines in {', '.join(sorted(names.get(v, v) for v in library))}: free plans can only use ElevenLabs' own voices through the API.")
            todo = [x for x in todo if x['voice'] not in library]
    chars = sum(len(x['text']) for x in todo)
    est = chars * model['_mult']
    print(f"Model {model['model_id']} (×{model['_mult']:g}) · {len(todo)} new lines of {len(sel)} selected · {chars:,} characters · ≈ {est:,.0f} credits")
    for x in todo[:20]:
        print(f"  {x['voice'][:10]}  {x['text'][:80]}")
    if len(todo) > 20:
        print(f'  … {len(todo) - 20} more')
    if not todo:
        print('Everything selected is already generated.')
        return
    if est > a.max_credits:
        sys.exit(f'That is more than --max-credits {a.max_credits}. Narrow it (--tier, --video) or raise the cap on purpose.')
    if est > left:
        sys.exit(f'Only {left:,} credits left in this period. Not spending.')
    if not a.go:
        print('\nDry run. Add --go to spend these credits.')
        return
    LINES.mkdir(parents=True, exist_ok=True)
    for n, x in enumerate(todo, 1):
        k = cache_key(x, model['model_id'], c)
        body = {'text': x['text'], 'model_id': model['model_id'], 'voice_settings': c['settings'], 'seed': c.get('seed')}
        if x['lang'] != 'en' and 'multilingual_v2' not in model['model_id']:
            body['language_code'] = x['lang']
        res = api('POST', f"/v1/text-to-speech/{x['voice']}/with-timestamps?output_format={c.get('output_format', 'mp3_44100_128')}", body)
        if have(k):
            (LINES / 'free-plan').mkdir(exist_ok=True)
            for ext in ('mp3', 'json'):
                (LINES / f'{k}.{ext}').rename(LINES / 'free-plan' / f'{k}.{ext}')
        (LINES / f'{k}.mp3').write_bytes(base64.b64decode(res['audio_base64']))
        meta = {'text': x['text'], 'voice': x['voice'], 'model': model['model_id'], 'lang': x['lang'], 'uses': x['uses'], 'plan': s.get('tier'), 'alignment': res.get('alignment') or res.get('normalized_alignment')}
        (LINES / f'{k}.json').write_text(json.dumps(meta, ensure_ascii=False))
        with LEDGER.open('a') as f:
            f.write(json.dumps({'at': time.strftime('%Y-%m-%dT%H:%M:%S'), 'key': k, 'chars': len(x['text']), 'credits_est': len(x['text']) * model['_mult'], 'model': model['model_id'], 'voice': x['voice'], 'uses': x['uses']}) + '\n')
        listen_copy(k, x, c)
        print(f"  [{n}/{len(todo)}] {x['text'][:70]}")
    print(f'Done. Listen in {LINES} before generating more.')


def cmd_place(a):
    """Copy lines to voice/<video>-NN.mp3 (+ .json) for every video whose lines are all generated."""
    c = conf()
    inv = inventory(c)
    ms = tts_models() if a.model == 'cheapest' else None
    model_for = lambda lang: pick_model(a.model, ms, {lang})['model_id'] if ms else a.model
    byvid = {}
    for x in inv:
        for vid, n in x['uses']:
            byvid.setdefault(vid, {})[n] = x
    ready, partial = [], []
    for vid, lines in sorted(byvid.items()):
        ks = {n: cache_key(x, model_for(x['lang']), c) for n, x in lines.items() if x['voice']}
        if len(ks) == len(lines) and all(have(k) for k in ks.values()):
            for n, k in ks.items():
                for ext in ('mp3', 'json'):
                    dst = VOICE / f'{vid}-{n:02d}.{ext}'
                    dst.write_bytes((LINES / f'{k}.{ext}').read_bytes())
            ready.append(vid)
        else:
            done = sum(1 for k in ks.values() if have(k))
            if done:
                partial.append(f'{vid} {done}/{len(lines)}')
    print('Ready for a voice render:', ', '.join(ready) or 'none yet')
    free = sorted({vid for vid in ready for n, x in byvid[vid].items() if made_free(cache_key(x, model_for(x['lang']), c))})
    if free:
        print('Made (partly) on the free plan, non-commercial use with attribution only:', ', '.join(free))
    if partial:
        print('Partly generated:', ', '.join(partial))


def cmd_srt(a):
    """Subtitles cut from the real voice: each line split into short cues timed by ElevenLabs' character timestamps."""
    cues = json.loads(Path(a.cues).read_text())
    timing = json.loads(re.sub(r'^window\.TIMING\s*=\s*|;\s*$', '', Path(a.timing).read_text().strip()))
    out, n = [], 1
    for i, l in enumerate(cues['lines']):
        meta_p = VOICE / f'{a.video}-{i + 1:02d}.json'
        lead = (timing[i] or {}).get('lead', 0.0) if i < len(timing) else 0.0
        base = l['t0'] + 0.12 - lead
        al = json.loads(meta_p.read_text()).get('alignment') if meta_p.exists() else None
        if not al:
            out.append((l['t0'] + 0.1, l['t0'] + l['dur'] - 0.15, l['vo']))
            continue
        ch, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
        chunk, c0 = '', None
        for j, c in enumerate(ch):
            if c0 is None and c.strip():
                c0 = st[j]
            chunk += c
            brk = (c in '.?!:;' and len(chunk.strip()) > 12) or (c == ',' and len(chunk.strip()) > 28) or (c == ' ' and len(chunk.strip()) > 40)
            if (brk or j == len(ch) - 1) and chunk.strip():
                out.append((base + c0, base + en[j] + 0.25, chunk.strip()))
                chunk, c0 = '', None
    def ts(t):
        ms = max(0, int(round(t * 1000)))
        return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'
    rows = []
    for k, (t0, t1, txt) in enumerate(out):
        if k + 1 < len(out):
            t1 = min(t1, out[k + 1][0] - 0.02)
        rows.append(f'{n}\n{ts(t0)} --> {ts(max(t1, t0 + 0.6))}\n{txt}\n')
        n += 1
    Path(a.out).write_text('\n'.join(rows), encoding='utf-8')
    print(f'Wrote {len(rows)} cues to {a.out}')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--project', help='project folder (default: SEEKFRAME_PROJECT or the current directory)')
    sp = p.add_subparsers(dest='cmd', required=True)
    sp.add_parser('status')
    sp.add_parser('models')
    v = sp.add_parser('voices'); v.add_argument('--search'); v.add_argument('--lang')
    pv = sp.add_parser('preview'); pv.add_argument('voice_id')
    for name in ('plan', 'gen'):
        x = sp.add_parser(name)
        x.add_argument('--tier', type=int)
        x.add_argument('--video')
        if name == 'gen':
            x.add_argument('--model', default='cheapest')
            x.add_argument('--max-credits', type=float, default=300)
            x.add_argument('--go', action='store_true')
    pl = sp.add_parser('place'); pl.add_argument('--model', default='cheapest')
    s = sp.add_parser('srt'); s.add_argument('video'); s.add_argument('--cues', required=True); s.add_argument('--timing', required=True); s.add_argument('--out', required=True)
    a = p.parse_args()
    if a.project:
        use_project(a.project)
    if a.cmd == 'gen' and a.tier is None and not a.video:
        sys.exit('Choose what to generate: --tier N and/or --video ID.')
    {'status': cmd_status, 'models': cmd_models, 'voices': cmd_voices, 'preview': cmd_preview, 'plan': cmd_plan, 'gen': cmd_gen, 'place': cmd_place, 'srt': cmd_srt}[a.cmd](a)


if __name__ == '__main__':
    main()
