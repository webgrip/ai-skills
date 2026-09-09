# Sources

Nothing here is committed except this manifest and `fetch.sh`. The extraction agents read fetched
text; the extracted result lives in `../extracts/`, which **is** committed, so re-fetching is only
needed to re-run an extraction from scratch.

Attribution and licence terms for everything used in the shipped catalogs are in
[`skills/humanize/NOTICE.md`](../../../skills/humanize/NOTICE.md).

## Skill repositories (git clone, MIT)

| Repo | Used for |
| --- | --- |
| [blader/humanizer](https://github.com/blader/humanizer) | 35 Wikipedia-derived patterns, voice matching |
| [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) | 20+ patterns, voice preservation, detect-only mode |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | rulebook, severity tiers, context profiles, regex detector |
| [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai) | Korean taxonomy, the translationese method, change-rate gates |
| [marmbiz/humanizer-de](https://github.com/marmbiz/humanizer-de) | German sister catalog, the shape a per-language adaptation takes |

## English lists

| Source | URL |
| --- | --- |
| Wikipedia, Signs of AI writing | <https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing> |
| Ossama Badr, tropes.fyi | <https://gist.github.com/ossa-ma/f3baa9d25154c33095e22272c631f5a1> |
| Ruben Hassid, the new em-dash | <https://substack.com/@ruben/note/c-313865032> |
| Ivo Velitchkov, 22 Claude clichés | <https://www.linkandth.ink/p/catalog-of-claude-cliches> |
| Matthew Vollmer, a field guide to AI tells | <https://matthewvollmer.substack.com/p/i-asked-the-machine-to-tell-on-itself> |
| Will Francis, how to stop Claude writing like an AI | <https://willfrancis.com/how-to-stop-claude-writing-like-an-ai/> |
| Sean Goedecke, why models use so many em-dashes | <https://www.seangoedecke.com/em-dashes/> |

## Dutch sources

| Source | URL |
| --- | --- |
| German Wikipedia, Anzeichen für KI-generierte Inhalte | <https://de.wikipedia.org/wiki/Wikipedia:Anzeichen_f%C3%BCr_KI-generierte_Inhalte> |
| VU ALP-gids, AI-teksten herkennen | <https://vu.nl/nl/over-de-vu/faculteiten/school-der-geesteswetenschappen/meer-over/alp-gids-ai-teksten-herkennen> |
| Jouw Copiloot, Signs of AI writing in het Nederlands | <https://jouwcopiloot.nl/algemeen/wikipedia-signs-of-ai-writing-is-mijn-geheime-wapen-voor-menselijkere-teksten/> |
| Onze Taal, ChatGPT en taalvragen | <https://onzetaal.nl/taalloket/chatgpt-en-taalvragen> |
| Frankwatching, irritante AI-woorden (2024) | <https://www.frankwatching.com/archive/2024/06/20/ai-woorden-die-we-niet-meer-willen-zien/> |
| Frankwatching, ChatGPT en het Nederlands (2023) | <https://www.frankwatching.com/archive/2023/11/28/chatgpt-nederlandse-taal/> |
| Frankwatching, LinkedIn grijpt in op AI-content (2026) | <https://www.frankwatching.com/archive/2026/05/31/linkedin-grijpt-in-op-ai-content/> |
| Rhinoz, typische AI-jeukwoorden | <https://rhinoz.nl/typische-ai-jeukwoorden/> |
| So-MC, 20 woorden waaraan je lezer AI herkent | <https://www.so-mc.nl/je-lezer-herkent-ai-content-aan-deze-20-woorden-kant-en-klare-prompt-die-je-direct-overneemt/> |
| Contentkantoor, AI-woorden herkennen | <https://contentkantoor.nl/ai-woorden-herkennen/> |
| Hulz, ChatGPT-teksten herkennen | <https://hulz.nl/blog/chatgpt-teksten-herkennen/> |
| Aikundig, AI-geschreven teksten herkennen | <https://aikundig.nl/hoe-herken-je-ai-geschreven-teksten-voorbeelden/> |
| Digiwijzer, AI-schrijven herkennen | <https://digiwijzer.nl/ai-schrijven-herkennen/> |
| Bikkelhart, 8 signalen | <https://www.bikkelhart.com/blog/8-signalen-om-ai-teksten-te-herkennen> |
| Wilfred Rubens, AI-teksten herkennen zonder technologie | <https://te-learning.nl/hoe-herken-je-ai-teksten-zonder-technologie/> |
| B2B Marketeers, ChatGPT-tekst herkennen | <https://www.b2bmarketeers.nl/ai/chatgpt-tekst-herkennen/> |
| Donna van de Ven, tekst van ChatGPT herkennen | <https://donnavandeven.nl/blog/ai/herken-tekst-geschreven-door-chatgpt/> |
| Oliver Op de Beeck, ChatGPT herkennen | <https://oliveropdebeeck.com/chatgpt-herkennen/> |
| Prompt Master, AI-tekst herkennen en opschonen | <https://prompt-master.nl/kennisbank/ai-tekst-herkennen-en-opschonen> |
| AI Slop Checker | <https://aislopchecker.nl/> |
| AI-tekstdetector | <https://aitekstdetector.nl/> |
| LinkAI, AI-tekst raakt de lezer niet | <https://www.linkai.nl/nieuws-artikelen/ai-schrijft-maar-jij-raakt-de-lezer> |
| PC-Active, AI-chatbots veranderen onze taal | <https://pcactive.nl/tech/denkwerk-ai-chatbots-veranderen-onze-taal> |

Three Frankwatching pages block `curl` and were captured through a fetching tool instead; their
extracted content sits in `../extracts/nl/`, and `fetch.sh` writes a placeholder naming the URL so
a re-run does not silently drop them.
