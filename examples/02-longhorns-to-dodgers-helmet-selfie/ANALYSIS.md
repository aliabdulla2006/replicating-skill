# Replication analysis: ig-DdUiyW_sted (Longhorns helmet selfie to door projection)

Source: https://www.instagram.com/p/DdUiyW_sted/ (competitor, Texas Longhorns)  |  Product: car-door-projector / baseball (LA Dodgers)  |  Date: 2026-10-05
Analyzer: `source/analysis.json`, `source/sheet-01.jpg`, `source/cuts.jpg`, full frames `source/full-1.0s.png`, `full-2.6s.png`, `full-3.4s.png`, `full-11.6s.png`

## STEP 1, scene analysis (doc 1)

- Total duration: 12 seconds (12.23 s).
- Six scenes, with 5 hard cuts at 2.37 / 3.83 / 6.20 / 7.53 / 8.50 s:
  - S1: selfie, a woman in a helmet gasping "Oh my god"
  - S2: POV in Target, a denim-sleeve hand pulls a box off a pallet display
  - S3: projector in hand, peeling the red film
  - S4: sticking it under the open door
  - S5: POV pulling the door handle
  - S6: night, the door opens and the logo projects on the asphalt
- Foreground to preserve:
  - S1: her face, gasp, hair, white ribbed tank top, gold chain.
  - S2: the denim sleeve and hand, the Target aisle, the shopper with the red cart, the pallet display.
  - S3-S6: the projector, the hands, the white car, the parking lot at dusk, the night car, the asphalt.
- Elements being replaced:
  - S1: the silver moto helmet with the Longhorn logo and orange flower decals, plus the orange bandana. These become a Dodger blue MLB batting helmet with the white LA logo, plus a Dodger blue bandana.
  - S2: every box front. Each has three parts: the team logo panel, the night SUV photo with its projected logo, and the brand strip "DRIVETOUCHDOWN / CAR DOOR LED PROJECTOR".
  - S6: the projected Longhorn becomes the LA disc (the same design as video 1).
- Text overlays (removed): "DO NOT show this to a Longhorns fan..." + emoji (0 to 8.5 s), "Link in bio" + emoji (8.5 to 12.2 s).
- Flags:
  - Team trademarks.
  - The "Oh my god" voice is lost because the output is silent (doc 1); re-add it in post if wanted.
  - The real Target store is kept.
  - Competitor brand "DRIVETOUCHDOWN": dropped from our boxes (default, no branding question per doc 2).

## Every visible face (skill step 4)

- The pulled box is seen front-on only (2.4 to 3.8 s).
- The display shows the fronts, the thin black right-side edges of the right column, and the dark top of the stack.
- The 2.6 s frame shows all of these, so one edit of it covers them. Change (1) still states that the sides and tops are plain black.

## Working notes

- Mode: doc 1 recreate+swap on the whole clip, MULTI-SCENE wording (S1, S2 and S6 each get different swaps). Duration 12.
- Refs: @video_1 = `source/reference-SILENT.mp4`; @image_1 = S1 helmet edit; @image_2 = S2 display edit; @image_3 = S6 projection edit.
- Ali: team = LA Dodgers again; headwear = team batting helmet.
