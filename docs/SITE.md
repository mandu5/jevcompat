# Recorded conformance explorer

`docs/index.html` is the native static documentation entry, published at
<https://mandu5.github.io/jevcompat/> from the `main` branch's `docs/` directory
using GitHub Pages. `.nojekyll` preserves the static files without processing.
README, SPEC, CLI, proxy and all existing report paths remain canonical.

## Serve and refresh

```sh
python3 docs/build_site.py --check
python3 -m http.server 19305 --bind 127.0.0.1 --directory docs
```

Open <http://127.0.0.1:19305/>. To update the presentation after a deliberate
change to the source reports or spec, run `python3 docs/build_site.py`, then
review its diff. The script copies all eight root `results/*/report.json`
records and extracts the normative SPEC excerpts. It includes SHA-256 hashes
of every source. It runs no conformance checks and makes no model requests.

## Interactions and evidence

- 8 × 48 matrix marks open the original result, all findings, the corresponding
  request and the original unmodified response text. Pass/skip states remain
  distinct. The full report and pinned run instructions are one link away.
- The compact matrix is keyboard navigable: Tab to enter it, arrow keys to move,
  Enter or Space to inspect. The dialog offers full-size previous/next controls;
  Escape closes it. All eight server reports are also linked in a readable list.
- Mobile keeps the matrix horizontally scrollable. The whole page does not
  overflow. The theme toggle preserves contrast in both light and dark modes.
- The September 24 date follows the original README's run-date convention;
  raw UTC timestamps remain unchanged in the included reports. The hero's 2/8
  statement is about those recorded runs, not the servers' present versions.

## Preserved entry points

| Destination | Entry |
| --- | --- |
| Specification | Original `SPEC.md` and its requirement anchors |
| Runs / raw artifacts | Original `results/<server>/` paths |
| Confidence study | Original image and `confidence_study.py` |
| CLI / CI / mock / proxy | Original README sections |
| New explorer | `docs/index.html`, `#overview`, `#runs`, `#confidence`, `#quick-start`, `#proxy` |

## Design and font provenance

This implements the A contract-weave scene selected on 2026-11-06, from the
local Design Studio study `design-studio-20261106/jevcompat.html?dir=a`
(`src/upgraded-scenes.js` / `.css`). The implementation is native HTML, CSS and
JavaScript; it does not embed the study or its selection/feedback shell.

Design Studio's starter and reference studies originated in company design
work. The user confirmed personal-project reuse review/approval on 2026-11-05.
That provenance is retained; the source design bundle is not being relicensed
as a new MIT library. No company data or proprietary typefaces are included.
The actual conformance records are this repository's original MIT artifacts.

Pretendard and Archivo are included locally with their original SIL Open Font
License texts in `assets/fonts/`. The Latin/common-glyph subset and Archivo
variable font were carried from the selected study. No CDN or third-party
JavaScript runtime is required.
