# Run log: barca-shelf-to-door-dodgers

Source: `products/car-door-projector/SaveClip.App_AQMg1R76j...mp4`  |  Product: car-door-projector / baseball (LA Dodgers)  |  Mode: doc 1 recreate+swap, multi-scene

## Refs (attach order = @image_N order)

| Slot | File | Made with | Approved |
|---|---|---|---|
| @video_1 | source/reference-SILENT.mp4 | analyzer | yes |
| @image_1 | refs/img-1-shelf-v1.png | NB Pro edit of source/full-clip1-0.0s.png | pending Ali |
| @image_2 | refs/img-2-projection-v1.png | NB Pro edit of source/full-clip6-8.6s.png | not fired |

## Image generations (ONE generation each)

| # | Slot | Doc(s) | Prompt file | Job id | Verdict |
|---|---|---|---|---|---|
| 1 | @image_1 | doc 2 image edit | prompts/img-1-shelf-v1.txt | Kie nano-banana-pro 265d99d8bf8a22b29b243628dd464928 | Good: LA boxes, Dodgers banner, white jersey, caption removed. Boxes show "LA" only (no script). |
| 2 | @image_2 | doc 2 image edit | prompts/img-2-projection-v1.txt | Kie nano-banana-pro faaf582581a8e5010cd9a61fb7104818 | Good: blue disc + white interlocking LA, real projected-light look, caption removed. |

Ali's choices: white home jersey, official Dodgers marks.

## Video generations (Kie bytedance/seedance-2-fast)

| V | Prompt file | Task id | Credits | Verdict / what failed (doc 2 FAILURE #) |
|---|---|---|---|---|
| V1 | prompts/video-v1.txt | 2599e492f927b5b801419044f6dc08c4 | 255 | Strong: all 6 scenes + cuts kept, LA box fronts, Dodgers banner + jersey, LA projection, zero text, silent. Flaw: small FCB crests survive on box SIDE panels (lifted box + boxes behind it), 1.5 to 2.3 s. Doc 2 FAILURE 3/9 class (detail not defined on faces the ref doesn't show). **APPROVED by Ali as is.** Saved to body-clips/shelf-grab-to-door-projection + final-clips/full-videos. v2 patch (prompts/video-v2.txt) not fired. Skill updated with the "every visible face" rule. |
