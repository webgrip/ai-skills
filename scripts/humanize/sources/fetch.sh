#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p repos lists nl

clone() {
  local repo=$1 dir=repos/${1#*/}
  [ -d "$dir" ] || git clone -q --depth 1 "https://github.com/$repo.git" "$dir"
  echo "  $dir $(git -C "$dir" log -1 --format='%h %cs')"
}

get() {
  local url=$1 out=$2
  curl -sfL -A "Mozilla/5.0 (Macintosh)" --max-time 40 "$url" -o "$out" \
    || echo "BLOCKED: fetch $url by hand; extracted content is in ../extracts/" > "$out"
}

echo "repos:"
clone blader/humanizer
clone petergyang/no-ai-slop
clone conorbronsdon/avoid-ai-writing
clone epoko77-ai/im-not-ai
clone marmbiz/humanizer-de

echo "english lists:"
get "https://en.wikipedia.org/w/index.php?title=Wikipedia:Signs_of_AI_writing&action=raw" lists/wikipedia-signs-of-ai-writing.wikitext
get "https://gist.githubusercontent.com/ossa-ma/f3baa9d25154c33095e22272c631f5a1/raw" lists/tropes-fyi.md
get "https://substack.com/@ruben/note/c-313865032" lists/ruben-hassid-new-em-dash.html
get "https://www.linkandth.ink/p/catalog-of-claude-cliches" lists/velitchkov-22-claude-cliches.html
get "https://matthewvollmer.substack.com/p/i-asked-the-machine-to-tell-on-itself" lists/vollmer-field-guide.html
get "https://willfrancis.com/how-to-stop-claude-writing-like-an-ai/" lists/willfrancis-prompt.html
get "https://www.seangoedecke.com/em-dashes/" lists/goedecke-em-dashes.html

echo "dutch sources:"
get "https://de.wikipedia.org/w/index.php?title=Wikipedia:Anzeichen_f%C3%BCr_KI-generierte_Inhalte&action=raw" nl/de-wikipedia-anzeichen-ki.wikitext
get "https://vu.nl/nl/over-de-vu/faculteiten/school-der-geesteswetenschappen/meer-over/alp-gids-ai-teksten-herkennen" nl/vu-alp-gids-nl.html
get "https://jouwcopiloot.nl/algemeen/wikipedia-signs-of-ai-writing-is-mijn-geheime-wapen-voor-menselijkere-teksten/" nl/jouwcopiloot-nl.html
get "https://onzetaal.nl/taalloket/chatgpt-en-taalvragen" nl/onzetaal-chatgpt-taalvragen.html
get "https://www.frankwatching.com/archive/2024/06/20/ai-woorden-die-we-niet-meer-willen-zien/" nl/frankwatching-2024-ai-woorden.html
get "https://www.frankwatching.com/archive/2023/11/28/chatgpt-nederlandse-taal/" nl/frankwatching-2023-nederlandse-taal.html
get "https://www.frankwatching.com/archive/2026/05/31/linkedin-grijpt-in-op-ai-content/" nl/frankwatching-2026-linkedin.html
get "https://rhinoz.nl/typische-ai-jeukwoorden/" nl/rhinoz-jeukwoorden.html
get "https://www.so-mc.nl/je-lezer-herkent-ai-content-aan-deze-20-woorden-kant-en-klare-prompt-die-je-direct-overneemt/" nl/somc-20-woorden.html
get "https://contentkantoor.nl/ai-woorden-herkennen/" nl/contentkantoor-ai-woorden.html
get "https://hulz.nl/blog/chatgpt-teksten-herkennen/" nl/hulz-herkennen.html
get "https://aikundig.nl/hoe-herken-je-ai-geschreven-teksten-voorbeelden/" nl/aikundig-herkennen.html
get "https://digiwijzer.nl/ai-schrijven-herkennen/" nl/digiwijzer-herkennen.html
get "https://www.bikkelhart.com/blog/8-signalen-om-ai-teksten-te-herkennen" nl/bikkelhart-8-signalen.html
get "https://te-learning.nl/hoe-herken-je-ai-teksten-zonder-technologie/" nl/rubens-zonder-technologie.html
get "https://www.b2bmarketeers.nl/ai/chatgpt-tekst-herkennen/" nl/b2bmarketeers-herkennen.html
get "https://donnavandeven.nl/blog/ai/herken-tekst-geschreven-door-chatgpt/" nl/donnavandeven-herkennen.html
get "https://oliveropdebeeck.com/chatgpt-herkennen/" nl/opdebeeck-herkennen.html
get "https://prompt-master.nl/kennisbank/ai-tekst-herkennen-en-opschonen" nl/promptmaster-opschonen.html
get "https://aislopchecker.nl/" nl/aislopchecker.html
get "https://aitekstdetector.nl/" nl/aitekstdetector.html
get "https://www.linkai.nl/nieuws-artikelen/ai-schrijft-maar-jij-raakt-de-lezer" nl/linkai-raakt-niet.html
get "https://pcactive.nl/tech/denkwerk-ai-chatbots-veranderen-onze-taal" nl/pcactive-denkwerk.html

python3 - <<'PY'
import glob
import html
import re
from html.parser import HTMLParser

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg", "nav", "header", "footer", "form"):
            self.skip += 1
        if tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "br", "tr"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg", "nav", "header", "footer", "form"):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)

for path in sorted(glob.glob("lists/*.html") + glob.glob("nl/*.html")):
    parser = Text()
    parser.feed(open(path, encoding="utf-8", errors="ignore").read())
    text = re.sub(r"\n\s*\n+", "\n\n", html.unescape("".join(parser.out))).strip()
    open(path[:-5] + ".txt", "w").write(text)
    print(f"  {len(text):7d} chars  {path[:-5]}")
PY
