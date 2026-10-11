# youtube-upload-kit

Everything between a finished video and a published one: thumbnail, title, description, chapters,
the upload form, the A/B test and what to read in Studio afterwards.

`scripts/sheet.mjs` turns an `<id>.upload.json` into the Studio form filled in, in the order the
upload dialog asks, and lists what breaks a rule (short chapters, thumbnail words that repeat the
title, a dead link, a free-plan voice set to public). `seekframe` writes that JSON after every render.

`scripts/thumb.mjs` renders thumbnails and Shorts covers from a frame of the video in the brand's own
fonts and colours, with up to three variants for YouTube's Test & Compare. Every rule in the skill
carries an evidence label in `research.md`: official YouTube documentation, large-sample data,
vendor claims and unverified folklore are kept apart.

Example prompts: "upload this so a few people can give feedback", "make a thumbnail I can A/B
test", "why does this get impressions but no clicks?".

Pairs with `seekframe` (making the video) and `devtool-social` (where to post it).
