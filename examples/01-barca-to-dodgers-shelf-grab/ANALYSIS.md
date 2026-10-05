# Replication analysis: barca-shelf-to-door-dodgers

Source: `products/car-door-projector/SaveClip.App_AQMg1R76j...mp4` (competitor, Barcelona niche)  |  Product: car-door-projector / baseball (LA Dodgers)  |  Date: 2026-10-05
Analyzer: `source/analysis.json`, `source/sheet-01.jpg`, `source/cuts.jpg`, full frames `source/full-clip1-0.0s.png`, `source/full-clip6-8.6s.png`

## STEP 1, scene analysis (doc 1)

- Total duration: 9 seconds (9.01 s).
- Six scenes, with 5 hard cuts at 2.27 / 3.70 / 4.70 / 6.03 / 7.37 s:
  - S1: store shelf grab
  - S2: projector in hand outside
  - S3: peeling the red adhesive film
  - S4: sticking it under the open door
  - S5: POV pulling the door handle
  - S6: night, door opens, logo projected on the asphalt
- Foreground to preserve:
  - S1: brunette woman with a high ponytail, her shocked face and both-arms grab, the box tipping into the cart, the shopping cart, the store shelving and ceiling.
  - S2-S5: the black square projector, the fair-skinned hands, the white car, the parking lot, the cloudy sky.
  - S6: the white car door, the door sill, the asphalt.
- Elements being replaced:
  - S1: every navy FCB-crest box on the shelves and in the cart, the red Barcelona banner top left, and the woman's black Nike tracksuit (becomes Dodgers fan gear).
  - S6: the projected FCB crest (becomes the LA Dodgers logo).
  - S2-S5: nothing.
- Text overlays (removed): "Barcelona fans RUN, don't walk to JD.." + emoji (0 to 6.0 s), "just kidding, we sell them" + emoji (6.0 to 9.0 s).
- Flags:
  - IP: the LA Dodgers logo and "Dodgers" script are MLB trademarks, the same situation as FCB in the source. Option: official logo, or a Dodgers-styled look without the exact marks.
  - Seedance/NB Pro may garble or refuse an exact logo.
  - The person looks AI-generated, not a real creator.

## Working notes

- Mode: doc 1 recreate+swap on the whole 9 s clip as @video_1. The swaps differ per scene, so the prompt uses doc 1's MULTI-SCENE EDGE CASE wording. The doc calls this a stretch case; the fallback is CapCut split + per-scene renders, but S1 (2.3 s) and S6 (1.6 s) are each under Seedance's 4 s minimum, so a single 9 s render is the practical route.
- The middle clips S2-S5 must still be regenerated, because the caption is burned into the source pixels. Doc 1 change (2) strips it.
- Audio: doc 1 change (3), completely silent (music added in post).
- Refs:
  - @video_1 = `source/reference-SILENT.mp4` (1.96 MB)
  - @image_1 = S1 frame edited to Dodgers boxes + banner + Dodgers outfit, caption removed (doc 2 image edit, Nano Banana Pro)
  - @image_2 = S6 frame edited to the projected Dodgers logo, caption removed (doc 2 image edit, Nano Banana Pro)
