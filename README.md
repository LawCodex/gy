# Guyana — Laws of Guyana (LawCodex)

Consolidated primary legislation of **Guyana** (the revised "Laws of Guyana", chapter by chapter) as plain
Markdown, converted from the official chapter PDFs published by the **Ministry of Legal Affairs** at
<https://mola.gov.gy/laws-of-guyana>.

Retrieved: 2026-10-13.

## Contents

| Directory | What | Files |
|---|---|---|
| `constitution/` | Constitution of the Co-operative Republic of Guyana Act, Cap. 1:01 (the Constitution is its Schedule) | 1 |
| `chapters/` | All other chapters listed on the Ministry's site (Caps 1:02 – 98:xx) | 458 |

Total: **459 of the 461 chapters** listed on mola.gov.gy (52 listing pages, volumes 1–18).
File names: `cap-VVV-NN-<slug>.md` (e.g. `cap-001-04-national-assembly-validity-of-elections-act.md`).

Front matter: `title`, `identifier` (Cap. number), `original_act` (as printed on the cover), `type`,
`revision` (the L.R.O. revision label printed on the cover page, e.g. `L.R.O. 1/2012` or `L.R.O. 1/2022`
— the Ministry's set mixes chapters last reprinted in the 2012 and 2022 revisions), `volume`, `source`,
`source_pdf`, `pages`, `retrieved`.

The chapter PDFs include the subsidiary legislation printed under each chapter (rules, regulations,
orders), which is therefore also contained in the Markdown files. Marginal notes are rendered as
*italic* lines before the paragraph they sit beside; section numbers in **bold**.

## Gaps

- Cap. 98:03 **Trade Unions Act** and Cap. 98:07 **Trade Union Recognition Act** — listed on the site,
  but the linked PDFs return HTTP 404 (no Internet Archive copy either).
- Acts passed after the revision date printed on each chapter are not merged in; the site does not
  provide point-in-time consolidation.
- Tables/forms are flattened to text (PDF text extraction); check the PDF for complex tables.

## Source and licence

Official texts of the Government of Guyana, published by the Ministry of Legal Affairs for public access;
no restrictive terms of use were found (robots.txt allows all). This is an unofficial conversion — the
official PDFs remain authoritative.

## Regenerate

```
python3 scripts/gy_fetch.py     # pages through /laws-of-guyana?page=N, downloads PDFs to ../_raw/gy/pdf
python3 scripts/gy_convert.py   # pdftotext -bbox-layout -> Markdown (scripts/gy_pdfmd.py)
```

Requires poppler (`pdftotext`, `pdfinfo`) and `scripts/requirements.txt`. PDFs are verified (header,
`%%EOF`, `pdfinfo`, Content-Length) before conversion.
