# Revised PDF companion audit — November 1, 2026

The current 144-page `From_the_PDP11_to_the_MSP430_Revised_Textbook_CLAUDE.pdf` was compared by extracted text with the earlier 128-page final PDF, now in `00/OLD Versions/`. The comparison found revised page design and navigation, a list of figures and tables, and instructional atlas figures integrated into the chapters. Source-listing text appears carried over; no intentional companion code or CSV change was identified from the comparison. Text extraction and token comparison are imperfect: figures, reading order, and minor differences require visual review. Existing source files remain educational candidates and their previous verification status has not changed.

`FULL_TEXT_EXPORT.txt` was generated from the current PDF using PyMuPDF, with PDF page numbers. It is a search aid rather than a layout-faithful replacement. The original atlas images remain separately available.

The existing `CORE_MANUSCRIPT.md`, `SOURCE_MANUSCRIPT_v1.md`, editorial scripts, and prior Word document are sources for the previous edition. The revised editable source and generation workflow were not supplied, so those materials have not been represented as synchronized or used to regenerate the revised PDF. A faithful editable rebuild requires the source used to create the revised edition.

On this Windows environment, `python -m unittest discover -s tests -v` passed all 11 Python tests. The previous C and supervisor results in `HOST_TEST_RESULTS.txt` are historical; no C compiler was found on PATH for a fresh run. No MSP430 target build or physical testing was performed. `RELEASE_QA.md` records the earlier 128-page release, not a new visual QA of this PDF.
