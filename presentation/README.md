# Final HTML Presentation

`index.html` is a self-contained, 13-slide, 16:9 presentation for the final
10-minute briefing. It displays one full-viewport slide at a time and does not
need a server, network connection, external font, or sibling runtime asset.

## Regenerate

The factual slide source is `slides.json`. Layout, styling, navigation, and HTML
generation are maintained in `build.mjs`. From the repository root, run:

```bash
node presentation/build.mjs
```

The builder validates that there are 11–13 slides, slide IDs are unique, and
the eight required course sections occur in order before replacing
`presentation/index.html`.

## Open

Double-click `presentation/index.html`, drag it into a browser, or run:

```bash
open presentation/index.html
```

The current slide is stored in the URL hash. A URL ending in `#slide-6` opens
slide 6 and returns to it after refresh.

## Controls

- Next: `→`, `↓`, Space, or `PageDown`
- Previous: `←`, `↑`, or `PageUp`
- First / last: `Home` / `End`
- Fullscreen: `F`; press `F` again to exit
- On screen: previous, next, and fullscreen buttons
- Trackpad or mouse: horizontal/vertical wheel gesture
- Touchscreen: horizontal swipe

The page counter and bottom progress bar update with every navigation method.
The deck honors `prefers-reduced-motion`.

## Print or save as PDF

Use the browser's Print command. The print stylesheet displays all 13 slides
and places each 16:9 slide on its own landscape page. Enable background graphics
if the browser offers that option.

## Verification

`BUILD_RECEIPT.json` records the final generated artifact and browser QA. The
deck was checked in real Chrome at 1920×1080 and 1280×800, plus a 1280×720 touch
context, for keyboard, buttons, rapid switching, pointer/touch swipe,
trackpad/wheel navigation, hash recovery, fullscreen, reduced motion, external
requests, browser errors, and content clipping. Print output was also rendered
and confirmed as 13 independent 960×540-point pages.
