# Tribunal Payment Templates — As-Is (Tribunals / SSCS)

This document records the spreadsheet templates currently used by tribunal systems to supply fee-paid judicial payment information to the JFEPS team. It is a record of the **as-is** process. Six templates were reviewed from the source pack `ji-input-docs/Tribunal-Payment-Templates/`. For each template the full structure is documented — sheets, layout, every column, header conventions, totals conventions and observed value vocabularies. No payment data, personal identifiers or fee amounts are reproduced; sample rows in the source files were inspected only to establish structure and field formats.

## At a Glance

| # | Template file | Flow (as named in file) | Jurisdiction / area | Format | Sheets | Layout style |
|---|---------------|-------------------------|---------------------|--------|--------|--------------|
| 1 | `14b - SSCS - from Crystal to BF.xls` | Crystal → BF | SSCS | Legacy `.xls` | `Sheet1` | Report banner + flat attendance rows |
| 2 | `18a - Courts - from OPT to BF - new template.xlsx` | OPT → BF | Courts (deputy / fee-paid judiciary) | `.xlsx` | `Itinerary` | Fee matrix — one column per judicial role, account-code row above headers |
| 3 | `19b - SEND - from Crystal to BF (1)KM (1).xlsx` | Crystal → BF | SEND | `.xlsx` | `Sheet1` | Report banner + flat attendance rows + grand-total footer |
| 4 | `JFS-1130-Sittings File - AST 1 (2).xlsx` | Sittings file → JEF import | AST (Asylum Support) | `.xlsx` | `JEF Import Sheet` | Import-ready claim lines, 22 named columns |
| 5 | `List Assist SSCS template.xlsx` | List Assist → JOH fee reconciliation | SSCS | `.xlsx` | `JOHFeeReconciliation` | Report header block + flat reconciliation rows |
| 6 | `Martha2 (1).xlsx` | Martha → payment file | Tribunal payment file (Martha) | `.xlsx` | `Payment File`, `Index` | Totals row above header + flat payment rows |

Three distinct shapes recur across the six templates:

1. **Crystal Reports attendance exports** (templates 1 and 3) — a one-line report banner, a header row, one row per panel-member attendance, fee in the final column.
2. **Fee-matrix / payment-file layouts** (templates 2 and 6) — one row per person per activity, with either fee-by-role columns (18a) or fee/travel/subsistence/misc columns (Martha2).
3. **System-import / reconciliation layouts** (templates 4 and 5) — column sets defined by the consuming system (JEF import schema; List Assist JOH fee reconciliation report).

---

## 1. SSCS — from Crystal to BF (`14b - SSCS - from Crystal to BF.xls`)

| Attribute | Detail |
|-----------|--------|
| **Source system** | Crystal Reports export (SSCS) |
| **Destination (as named)** | BF |
| **File format** | Legacy Excel 97-2003 (`.xls`) |
| **Sheets** | `Sheet1` (single sheet) |
| **Banner row** | Row 1, column A: `Report B - Panel Members Attendance for period DD/MM/YYYY - DD/MM/YYYY (Printed on DD/MM/YYYY)` |
| **Header row** | Row 2 |
| **Data rows** | Row 3 onwards, one row per panel-member attendance |
| **Totals** | None — no footer or grand-total row |
| **Granularity** | One row per member per session attended |

### Column structure

| Col | Heading | Type / format | Notes |
|-----|---------|---------------|-------|
| A | `Name` | Text | Panel member name |
| B | `NINO` | Text | National Insurance number; mixed upper/lower case observed in the source — no case normalisation applied by the export |
| C | `ATTENDED` | Text flag | `Y` |
| D | `Date` | **Text**, `MM/DD/YYYY` | Stored as a text string in US month-first order, not as an Excel date |
| E | `Period` | Text enum | `Morning`, `Afternoon` |
| F | `Session Category` | Text | Pattern `NN - Category`; values carry **leading and trailing spaces** in the export |
| G | `Venue` | Text | Venue name (court/venue) |
| H | `Cost Centre` | Text | Pattern `NNNN-NNNNNNNN` (4-digit prefix, hyphen, 8-digit cost centre) |
| I | `Account Code` | Number | 10-digit general-ledger account code, stored as a numeric value |
| J | `Fee` | Number | Fee amount, decimal |

### Notes

- The worksheet carries roughly 4,200 formatted-but-empty rows beyond the content (an artefact of the Crystal Reports export); only the banner, header and data rows hold values.
- The reporting period and print date are embedded in the row-1 banner text rather than in dedicated cells.

---

## 2. Courts — from OPT to BF, new template (`18a - Courts - from OPT to BF - new template.xlsx`)

| Attribute | Detail |
|-----------|--------|
| **Source system** | OPT |
| **Destination (as named)** | BF |
| **File format** | `.xlsx` |
| **Sheets** | `Itinerary` (single sheet) |
| **Account-code row** | Row 3 — a 10-digit account code sits **above each fee column** (H–P); see mapping below |
| **Header row** | Row 4 |
| **Data rows** | Row 5 onwards |
| **Totals** | None |
| **Granularity** | One row per person per activity per date; the fee amount is placed in the **column matching the judicial role** |

### Column structure

| Col | Heading | Type / format | Notes |
|-----|---------|---------------|-------|
| A | `Payroll ID` | Mixed | Numeric IDs and `PAYnnnnnn`-style references both observed |
| B | `Name` | Text | Judicial office holder name |
| C | `Cost Centre` | Number | 8-digit cost centre |
| D | `Analysis` | — | Present in the header; unpopulated in the template sample |
| E | `Activity` | Text enum | `Sitting`, `Appraisal`, `Sickness` |
| F | `Date` | Excel date | Displayed `mm-dd-yy` |
| G | `Session Length` | Text enum | `All day` |
| H | `Deputy District Judge (DDJ)` | Number | Fee amount when the role is DDJ |
| I | `Recorder` | Number | Fee amount when the role is Recorder |
| J | `Deputy Circuit Judge (DCJ)` | Number | Fee amount when the role is DCJ |
| K | `Deputy/Retired High Court Judge (DHCJ)` | Number | Fee amount when the role is DHCJ |
| L | `Deputy District Judge Mags. Court (DDJ MC)` | Number | Fee amount when the role is DDJ MC |
| M | `Deputy Masters` | Number | Fee amount when the role is Deputy Master |
| N | `Retired Lord Justice` | Number | Fee amount when the role is Retired Lord Justice |
| O | `Appraisal` | Number | Appraisal fee amount |
| P | `Sick Pay` | Number | Sick-pay amount |
| Q | *(no heading)* | Text | Unlabelled reference column; carries a source/batch reference string combining an office number, source system, location and date (e.g. `NN OPT <LOCATION> D/M/YY`) |

### Account-code row (row 3)

Each fee column carries its general-ledger account code in row 3, directly above the column heading:

| Fee column | Heading | Account code |
|------------|---------|--------------|
| H | Deputy District Judge (DDJ) | `5111102022` |
| I | Recorder | `5111102024` |
| J | Deputy Circuit Judge (DCJ) | `5111102027` |
| K | Deputy/Retired High Court Judge (DHCJ) | `5111102025` |
| L | Deputy District Judge Mags. Court (DDJ MC) | `5111102021` |
| M | Deputy Masters | `5111102028` |
| N | Retired Lord Justice | `5111102023` |
| O | Appraisal | `5224102116` |
| P | Sick Pay | `5111102045` |

### Notes

- Exactly one fee column is populated per row — the row's judicial role is implied by which column holds the amount, plus the `Activity` value (a `Sickness` activity row still places its amount in a role column).
- Rows 1–2 are empty; the sheet's content starts at the row-3 account codes.
- A single person (same `Payroll ID`) can appear on multiple rows for different activities and dates.

---

## 3. SEND — from Crystal to BF (`19b - SEND - from Crystal to BF (1)KM (1).xlsx`)

| Attribute | Detail |
|-----------|--------|
| **Source system** | Crystal Reports export (SEND) |
| **Destination (as named)** | BF |
| **File format** | `.xlsx` |
| **Sheets** | `Sheet1` (single sheet) |
| **Banner row** | Row 1 (see layout below) |
| **Header row** | Row 2 |
| **Data rows** | Row 3 onwards |
| **Totals** | Grand-total footer row immediately after the last data row (see layout below) |
| **Granularity** | One row per panel member per session attended |

### Banner row layout (row 1)

| Cell(s) | Content |
|---------|---------|
| B1 | Literal text `PANEL MEMBERS ATTENDANCE  FOR WEEK ENDING` |
| G1, H1 | Week-ending date (Excel date, duplicated across both cells) |
| I1 | Literal text `From` |
| J1 | Period-from date (Excel date) |
| K1 | Literal text `To` |
| L1 | Period-to date (Excel date) |
| M1 | Literal text `REPORT B` |

### Column structure

| Col | Heading | Type / format | Notes |
|-----|---------|---------------|-------|
| A | `Name` | Text | Panel member name |
| B | `NINO` | Text | National Insurance number; mixed case and embedded tab characters observed in the source data |
| C | `ATTENDED` | Text flag | `Y` |
| D | `Date` | Excel date | Attendance date |
| E | `Period` | Text enum | `All Day`, `Afternoon`; blank on some rows |
| F | `Session ID` | Number | 9-digit session identifier |
| G | `Venue` | Text | Pattern `SEND - <Location>` |
| H | `BEC` | Number | 8-digit cost-centre code (Budget Expenditure Code) |
| I | `NAC` | Number | 10-digit account code (Nominal Account Code) |
| J | `Fee` | Number | Fee amount, decimal |

### Grand-total footer row layout

The footer row sits directly below the last data row and mixes labels and figures across the same columns:

| Cell | Content |
|------|---------|
| A | Literal text `Grand Total:` |
| C | Literal text `Grand Total` |
| D | Literal text `Total Number Attended` |
| E | Count of attendances (number) |
| I | Total fees (number) |
| J | Literal text `Total Fees Paid` |
| K | Total fees (number, repeated) |
| L | Literal text `Total Number of Records` |
| M | Record count (number) |

### Notes

- The footer's totals (attendance count, record count) reflect the full source report, not just the rows present in the sheet — the template sample carries totals far larger than its visible row count, indicating the file is a truncated extract of a bigger weekly report.
- One stray residual value sits in column J on the row below the footer in the template sample.
- The `BEC` / `NAC` pair is this template's naming for what `14b` calls `Cost Centre` / `Account Code`.

---

## 4. AST Sittings file — JEF import (`JFS-1130-Sittings File - AST 1 (2).xlsx`)

| Attribute | Detail |
|-----------|--------|
| **Source / purpose** | Sittings file for AST (Asylum Support Tribunal), shaped as a **JEF import sheet** — the column set is the JEF expense-import schema |
| **File format** | `.xlsx` |
| **Sheets** | `JEF Import Sheet` (single sheet) |
| **Header row** | Row 1 |
| **Data rows** | Row 2 onwards, one row per expense claim line |
| **Totals** | None |
| **Granularity** | One row per claimant per sitting claim |

### Column structure

All 22 named columns of the JEF import schema are present. Several are part of the schema but left unpopulated in this sittings-file usage — these are marked below.

| Col | Heading | Type / format | Populated in template | Notes |
|-----|---------|---------------|-----------------------|-------|
| A | `ExpenseTypeName` | Text | Yes | JEF expense-type key; pattern `FtT-SEC-AS-Judge-LW-A Sitting` |
| B | `ClaimantEmailAddress` | Text | Yes | Claimant identified by email address |
| C | `ClaimDate` | **Text**, `MM/DD/YYYY` | Yes | Stored as text in US month-first order |
| D | `Description` | Text | Yes | Pattern `AST Sitting DD-MM-YYYY` |
| E | `BusinessUse` | Text | Yes | Carries the case reference list: `Case Reference Number: NNNNNX, NNNNNX, …` |
| F | `ProjectCode` | — | No | Schema column, blank in this usage |
| G | `TaskCode` | — | No | Schema column, blank in this usage |
| H | `Quantity` | Number | Yes | Number of sessions claimed (integer) |
| I | `Rate` | — | No | Schema column, blank in this usage |
| J | `Gross` | Number | Yes | Gross claim amount |
| K | `VATCode` | — | No | Schema column, blank in this usage |
| L | `VAT` | — | No | Schema column, blank in this usage |
| M | `CurrencyIsoCode` | Text | Yes | `GBP` |
| N | `DefaultCurrencyVAT` | — | No | Schema column, blank in this usage |
| O | `ActualDistance` | — | No | Schema column, blank in this usage |
| P | `VehicleName` | — | No | Schema column, blank in this usage |
| Q | `UserDefinableNumber` | — | No | Schema column, blank in this usage |
| R | `VATReceiptOption` | Text enum | Yes | `No receipt required (Fees)` |
| S | `BankAccountName` | — | No | Schema column, blank in this usage |
| T | `SelectUsers` | — | No | Schema column, blank in this usage |
| U | `Tag:Appointment` | Text | Yes | Appointment tag; pattern `FtT-SEC-Asylum Support-Judge-LW` |
| V | `Tag:Hearing Venue` | Text | Yes | Hearing-venue tag, e.g. venue-name string |

### Notes

- This is the only template in the set that identifies the claimant by **email address** rather than by name + NINO or payroll reference.
- It is also the only template carrying **case reference numbers** (in `BusinessUse`).
- The two `Tag:` columns are JEF tag-typed fields (tag category embedded in the column name after the colon).
- A 23rd column position exists in the sheet's used range but has no heading and no values.

---

## 5. List Assist SSCS template (`List Assist SSCS template.xlsx`)

| Attribute | Detail |
|-----------|--------|
| **Source system** | List Assist |
| **Purpose (as named in sheet)** | JOH Fee Reconciliation |
| **File format** | `.xlsx` |
| **Sheets** | `JOHFeeReconciliation` (single sheet) |
| **Title row** | Row 1, column A: literal text `JOH Fee Reconciliation` |
| **Report-metadata row** | Row 2, merged across `A2:G2`: two lines — `Report generator name: <email address>` and `Period Covered: DD/MM/YYYY To DD/MM/YYYY` |
| **Header row** | Row 5 (rows 3–4 are empty); headers occupy columns **B–R**, column A is unused |
| **Data rows** | Row 6 onwards |
| **Totals** | None |
| **Granularity** | One row per JOH (judicial office holder) per session |

### Column structure

| Col | Heading | Type / format | Populated in template | Notes |
|-----|---------|---------------|-----------------------|-------|
| A | *(unused)* | — | — | No heading, no values |
| B | `Member Name` | Text | Yes | Format `Surname, Forename` |
| C | `JOH Unique ID` | Text | Yes | 8-digit identifier stored as text |
| D | `Role` | Text | Yes | e.g. `Tribunal Member Medical` |
| E | `ATTENDED` | Text flag | Yes | `Y` |
| F | `Date` | Excel date | Yes | Displayed `mm/dd/yyyy` |
| G | `Period` | Text enum | Yes | `Morning` |
| H | `Session Category` | Text | Yes | Pattern `SSCS NN AM/PM` |
| I | `Region` | Text | Yes | e.g. region name |
| J | `Venue` | Text | Yes | Pattern `SSCS <Location>` |
| K | `Room` | Text | Yes | Pattern `<Location> Courtroom NN` |
| L | `Cost Centre` | Text | Yes | Pattern `NNNN-NNNNNNNN` (same shape as template 1) |
| M | `Account Code` | Number | Yes | 10-digit account code |
| N | `Fee` | Number | Yes | Fee amount, decimal |
| O | `Session Start Time` | — | No | Header present; unpopulated in the template sample |
| P | `Session End Time` | — | No | Header present; unpopulated in the template sample |
| Q | `JOH Arrival Time` | — | No | Header present; unpopulated in the template sample |
| R | `JOH Departure Time` | — | No | Header present; unpopulated in the template sample |

### Notes

- This is the richest attendance layout in the set: it adds `Region`, `Room`, `Session Category` and four session/arrival timing columns that no other template carries.
- The report generator (a named user's email address) and the period covered are embedded in the merged row-2 cell rather than in separate labelled cells.
- The `JOH Unique ID` replaces NINO as the person identifier — the only attendance-style template not using NINO.

---

## 6. Martha payment file (`Martha2 (1).xlsx`)

| Attribute | Detail |
|-----------|--------|
| **Source system** | Martha |
| **File format** | `.xlsx` |
| **Sheets** | `Payment File` (primary), `Index` (secondary — see below) |
| **Totals row** | Row 3 — sits **above** the header row: label `TOTAL:` in column I, then totals for FEE, TRAVEL, SUBSISTENCE, MISC and TOTAL in columns J–N |
| **Header row** | Row 4 (rows 1–2 are empty) |
| **Data rows** | Row 5 onwards |
| **Granularity** | One row per member per activity per date range |

### `Payment File` sheet — column structure

| Col | Heading | Type / format | Notes |
|-----|---------|---------------|-------|
| A | `MEMBER (Name Only)` | Text | Member name; heading explicitly constrains the field to name only |
| B | `PAY REF` | Mixed | Numeric references and `PAYnnnnnn`-style references both observed |
| C | `ROLE` | Text enum | `Member (Lay)`, `Member (Medical)`, `Tribunal Judge` |
| D | `SALARY` | Text enum | `Fee Paid` |
| E | `BEC` | Number | 8-digit cost-centre code |
| F | `ACTIVITY` | Text enum | `Sitting`, `Other` |
| G | `START` | Excel date | Activity start date, displayed `mm-dd-yy` |
| H | `END` | Excel date | Activity end date — can span a multi-day range |
| I | `CLAIM` | Text enum | `Expected (Full)` |
| J | `FEE` | Number | Fee amount |
| K | `TRAVEL` | Number | Travel amount |
| L | `SUBSISTENCE` | Number | Subsistence amount |
| M | `MISC` | Number | Miscellaneous amount |
| N | `TOTAL` | Number | Row total |

### Totals row layout (row 3, above the headers)

| Cell | Content |
|------|---------|
| I3 | Literal text `TOTAL:` |
| J3 | Sum of `FEE` column |
| K3 | Sum of `TRAVEL` column |
| L3 | Sum of `SUBSISTENCE` column |
| M3 | Sum of `MISC` column |
| N3 | Sum of `TOTAL` column |

The totals are stored as plain values, not as live formulas.

### `Index` sheet

The `Index` sheet repeats the same 14-column shape as `Payment File` but with **no header row and no totals row** — data starts at row 2. The template sample's rows include zero-value and **negative** fee entries alongside unchanged totals, consistent with a working/adjustments area rather than a second payment file. Its role is not labelled anywhere in the workbook.

### Notes

- Martha2 is the only template in the set that splits payment into **FEE / TRAVEL / SUBSISTENCE / MISC / TOTAL** components and the only one with a claim-status field (`CLAIM`).
- The same member can appear on multiple rows with different `PAY REF` values in the sample, suggesting the reference is per-claim rather than per-person.
- The `Payment File` sheet's used range extends to ~9,100 formatted rows; only the totals row, header row and data rows hold values.

---

## Cross-template observations

### Common concepts, different names

The same underlying concepts appear under different column names across the six templates:

| Concept | 14b SSCS (Crystal) | 18a Courts (OPT) | 19b SEND (Crystal) | JFS-1130 AST (JEF) | List Assist SSCS | Martha2 |
|---------|--------------------|------------------|--------------------|--------------------|------------------|---------|
| Person identifier | `NINO` | `Payroll ID` | `NINO` | `ClaimantEmailAddress` | `JOH Unique ID` | `PAY REF` |
| Person name | `Name` | `Name` | `Name` | — (email only) | `Member Name` | `MEMBER (Name Only)` |
| Role | — | implied by fee column | — | `ExpenseTypeName` / `Tag:Appointment` | `Role` | `ROLE` |
| Attendance flag | `ATTENDED` | — | `ATTENDED` | — | `ATTENDED` | — |
| Activity type | — | `Activity` | — | `Description` | — | `ACTIVITY` |
| Date | `Date` (text) | `Date` | `Date` | `ClaimDate` (text) | `Date` | `START` / `END` |
| Session period | `Period` | `Session Length` | `Period` | `Quantity` (count) | `Period` | — |
| Venue | `Venue` | — | `Venue` | `Tag:Hearing Venue` | `Venue` + `Room` + `Region` | — |
| Cost centre | `Cost Centre` | `Cost Centre` | `BEC` | — | `Cost Centre` | `BEC` |
| Account code | `Account Code` | row-3 code per fee column | `NAC` | — | `Account Code` | — |
| Fee | `Fee` | one column per role | `Fee` | `Gross` | `Fee` | `FEE`…`TOTAL` split |
| Session/category | `Session Category` | — | `Session ID` | `BusinessUse` (case refs) | `Session Category` | — |

### Structural inconsistencies in the as-is process

- **Person identification is not standardised** — four different identifier schemes are in use (NINO, payroll/pay reference, JOH unique ID, email address), and NINO values arrive without case normalisation.
- **Date handling is inconsistent** — two templates store dates as text in US `MM/DD/YYYY` order (14b, JFS-1130); the rest use native Excel dates with varying display formats (`mm-dd-yy`, `mm/dd/yyyy`).
- **Cost-centre representation varies** — `NNNN-NNNNNNNN` text in 14b and List Assist versus a bare 8-digit number (`Cost Centre`/`BEC`) in 18a, 19b and Martha2.
- **Account-code placement varies** — a per-row column (14b, 19b, List Assist) versus a per-column header value (18a) versus absent entirely (JFS-1130, Martha2).
- **Totals conventions vary** — none (14b, 18a, JFS-1130, List Assist), a footer row below the data (19b), or a totals row above the header (Martha2).
- **Header position varies** — row 1 (JFS-1130), row 2 (14b, 19b), row 4 (Martha2), row 5 starting at column B (List Assist), row 4 with an account-code row above (18a).
- **Export artefacts** — the Crystal-sourced files carry thousands of formatted-but-empty rows; values arrive with leading/trailing spaces and embedded tab characters.

---

> Source pack: `ji-input-docs/Tribunal-Payment-Templates/` (6 files, reviewed 2026-06-12). Structure was extracted programmatically from each workbook (sheets, used ranges, merged cells, headers, cell formats); no payment data is reproduced in this document.
