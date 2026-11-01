# Final editorial release QA — 2026-10-31

## Artifact checks

- PDF rendered from editable Word manuscript with LibreOffice; 128 pages.
- Entire 128-page DOCX separately rendered to PNGs for visual consistency check.
- Representative cover, title page, contents, chapter, worksheet, appendix, and final pages reviewed in an image contact sheet.
- All 128 PDF pages checked programmatically for text blocks crossing page bounds: zero such blocks.
- PDF bookmark navigation present (428 outline nodes, including subsections and worksheets).
- Table of contents checked after pagination pass: 14 chapters listed under the intended Part I/II/III headings; page labels resolved.
- Cover image included separately, no external or proprietary font files included.
- Host-side tests executed with Python 3 and C11 `cc -Wall -Wextra -Werror -pedantic`.
- Eleven Python unit tests passed, C DS18B20 CRC/decoding test passed, C hysteresis controller test passed, and host supervisor demonstration ran.

## Limitations carried into the book

- No available MSP430 target compiler was used in this environment; target firmware and on-target compiler warnings have not been verified.
- No PDP-11 assembler or physical PDP-11 run demonstrated.
- No MSP430G2553 physical board, Pico firmware, GNSS reference, or DS18B20 sensor measurement was obtained in this release.
- Timing candidates, especially the 1-Wire code, require scope/logic-analyzer validation and review before actual use.
- Industrial-control safety and fail-safe behavior are demonstrations, not qualified industrial systems.

## Source organization

- `CORE_MANUSCRIPT.md` is the editable core exposition.
- `editorial/final_expansions.py` contains the final supplementary chapter prose.
- `editorial/make_figures_and_labs.py` contains the classroom laboratory and diagram data.
- `editorial/build_final_book.py` generates the DOCX and PDF, including instructor worksheets and appendices.
- `FULL_TEXT_EXPORT.txt` is a plain-text export of all 128 PDF pages (includes generated material).

This report records observed editorial and host-side verification; it is not a physical-hardware certification.
