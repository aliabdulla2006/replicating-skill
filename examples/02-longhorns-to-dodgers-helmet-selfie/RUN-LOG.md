# Run log: ig-DdUiyW_sted (Longhorns helmet selfie to door projection, LA Dodgers)

Source: https://www.instagram.com/p/DdUiyW_sted/ (downloaded by the analyzer from the link)  |  Product: car-door-projector / baseball (LA Dodgers, brand Walk-Off Lights)  |  Mode: doc 1 recreate+swap, multi-scene

## Refs (attach order = @image_N order)

| Slot | File | Made with | Approved |
|---|---|---|---|
| @video_1 | source/reference-SILENT.mp4 | analyzer | yes |
| @image_1 | refs/img-1-helmet-v1.png | Kie NB Pro edit of source/full-1.0s.png | yes |
| @image_2 | refs/img-2-display-v2.png | Kie NB Pro patch edit of img-2-display-v1.png | yes |
| @image_3 | refs/img-3-projection-v1.png | Higgs nano_banana_pro (ran as nano_banana_2) edit of source/full-11.6s.png | pending |

## Image generations (ONE generation each)

| # | Slot | Doc(s) | Prompt file | Job id | Verdict |
|---|---|---|---|---|---|
| 1 | @image_1 | doc 2 edit | prompts/img-1-helmet-v1.txt | Kie 5766726c345fd569d1405be0e9511cb2 | Good: blue batting helmet + LA, eyes visible, blue paisley bandana, caption removed |
| 2 | @image_2 | doc 2 edit | prompts/img-2-display-v1.txt | Kie b5b8425e90e098242a7d32ff9cd46e18 | Boxes swapped but competitor brand "DRIVETOUCHDOWN" survived (doc 2 FAILURE 9; naming it in DO NOT likely reinforced it, RULE 1) |
| 3 | @image_2 | doc 2 patch edit on v1 | prompts/img-2-display-v2.txt | Kie 8e5dc665ddac11eeb1e9d53a5239cd05 | Good: front + 2nd row read "WALK-OFF LIGHTS / CAR DOOR LED PROJECTOR"; far bottom row garbled (background) |
| 4 | @image_3 | doc 2 edit | prompts/img-3-projection-v1.txt | Higgs 4040da29-00d9-42ac-bcf2-66dd468d15dd | Good logo; framing slightly wider, warm light pool weaker than source |

Ali's choices: team LA Dodgers; team batting helmet; brand Walk-Off Lights.

## Video generations (Kie bytedance/seedance-2-fast)

| V | Prompt file | Task id | Credits | Verdict / what failed (doc 2 FAILURE #) |
|---|---|---|---|---|
| V1 | prompts/video-v1.txt | c85994954632598338d700c85595d2f2 | 360 | Strong: helmet + bandana + eyes, Walk-Off Lights display (front box reads "WALK-OFF LIGHTS"; small "LED PROJECTOR" line slightly garbled), LA projection in the wide + top-down night shots, zero text, silent. FLAW: orange Longhorn survives in the door-opening night shot 8.6 to 9.3 s (a shot the cut detector missed in dark footage, no ref covered it). Analyzer + skill updated (soft cuts, "every shot it appears in"). |
