import json, sys
c = json.load(open(sys.argv[1]))
def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
out = []
for i, l in enumerate(c['lines'], 1):
    out.append(f"{i}\n{ts(l['t0'] + 0.1)} --> {ts(l['t0'] + l['dur'] - 0.15)}\n{l['vo']}\n")
open(sys.argv[2], 'w').write('\n'.join(out))
