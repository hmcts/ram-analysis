# Judicial Itineraries (JI) - Integration Dependencies

This document maps the integration flows between the Judicial Itineraries (JI) system and external systems, describing what data moves, how it moves, and who is involved at each step.

## At a Glance

| # | Flow | Source | Destination | Data | Mechanism | Frequency | Criticality |
|---|------|--------|-------------|------|-----------|-----------|-------------|
| 1 | [Judge Master Data](#flow-1--judge-master-data-elinks--hr--ji) | eLinks, HR Records | JI | Judge profiles, working patterns, contractual sitting days | Manual entry / manual copy | On change | High |
| 2 | [Planned Activity Capture](#flow-2--planned-activity-capture-listing-systems--ji) | Court Listing Systems | JI | Planned sittings, work types, daily judicial activity | Manual copy into JI | Daily | Medium |
| 3 | [Sitting & Booking Confirmation](#flow-3--sitting--booking-confirmation-court-staff--ji) | Court Staff | JI | Confirmed sittings, actual work types, session durations | Manual entry via JI UI | Daily | High |
| 4 | [Absence & Vacancy Management](#flow-4--absence--vacancy-management-courts--rsu--ji) | Courts, RSU | JI | Absence requests, vacancy creation, NTBF decisions | Manual entry via JI UI with approval workflow | Event-driven | High |
| 5 | [Fee-Paid Payment Export](#flow-5--fee-paid-payment-export-ji--jfeps--liberata) | JI | JFEPS, Liberata | Payment files for fee-paid judges | Excel export, email, manual upload | Weekly | Critical |
| 6 | [Payment Reconciliation](#flow-6--payment-reconciliation-jfeps--ji) | JFEPS | JI | Payment confirmations, discrepancies | Manual flagging in JI | Ongoing | Medium |
| 7 | [Management Information & Reporting](#flow-7--management-information--reporting-ji--dai) | JI | DA&I | Sitting days, utilisation, vacancy/absence analysis | Excel / PDF report exports | Reporting cycles | High |
| 8 | [Notifications & Communications](#flow-8--notifications--communications-ji--hmcts-email) | JI | HMCTS Email, Judges, Court Staff | Itineraries, booking confirmations, absence alerts, payment files | Automated email (some batch) | Event-driven | High |

---

## Flow Index

1. [Judge Master Data (eLinks / HR -> JI)](#flow-1--judge-master-data-elinks--hr--ji)
2. [Planned Activity Capture (Listing Systems -> JI)](#flow-2--planned-activity-capture-listing-systems--ji)
3. [Sitting & Booking Confirmation (Court Staff -> JI)](#flow-3--sitting--booking-confirmation-court-staff--ji)
4. [Absence & Vacancy Management (Courts / RSU -> JI)](#flow-4--absence--vacancy-management-courts--rsu--ji)
5. [Fee-Paid Payment Export (JI -> JFEPS -> Liberata)](#flow-5--fee-paid-payment-export-ji--jfeps--liberata)
6. [Payment Reconciliation (JFEPS -> JI)](#flow-6--payment-reconciliation-jfeps--ji)
7. [Management Information & Reporting (JI -> DA&I)](#flow-7--management-information--reporting-ji--dai)
8. [Notifications & Communications (JI -> HMCTS Email)](#flow-8--notifications--communications-ji--hmcts-email)

---

## Flow 1 -- Judge Master Data (eLinks / HR -> JI)

Judge profile and working pattern data originates in external HR systems and the eLinks Judicial Database, and is manually entered into JI by RSU users. JI is not the system of record for judge employment data; it reflects what has been agreed elsewhere.

| Attribute | Detail |
|-----------|--------|
| **Sources** | eLinks (Judicial Database), HR / administrative records |
| **Destination** | JI (Manage Judges screens) |
| **Data** | Judge names, titles, contact details, judge type (salaried / fee-paid), base location, roles, authorisations, tickets, working patterns (days, locations, work types), contractual sitting days, part-time arrangements, jurisdictional split, retirement dates, payroll numbers, fee payment status |
| **Mechanism** | Manual entry by RSU / judicial team users. The SRS states an eLinks integration requirement (NFR-3: "The system shall support eLinks integration for importing judiciary data") but the technical mechanism is not implemented. |
| **Frequency** | On change -- new judge onboarding, base court transfers, part-time conversions, role updates |
| **Users involved** | RSU Admin, Regional (Full Access) users |
| **Criticality** | High -- all itineraries, bookings, and reports depend on accurate judge data |

![Flow 1 — HR/Admin records and the eLinks Judicial Database are manually copied by RSU users into JI's Manage Judges screen, which feeds Working Patterns and auto-generates judge itineraries](flow-1-judge-master-data.png)

<!--
Diagram source (Mermaid). Regenerate flow-1-judge-master-data.png with:
  mmdc -i flow-1-judge-master-data.mmd -o flow-1-judge-master-data.png -b white -s 3
Use <br/> for label line breaks (Mermaid renders a literal \n as text).

flowchart LR
    subgraph Source Systems
        HR[HR / Admin Records]
        EL[eLinks<br/>Judicial Database]
    end

    subgraph Users
        RSU[RSU / Judicial<br/>Team User]
    end

    subgraph JI
        MJ[Manage Judges<br/>Screen]
        WP[Working Patterns]
        ITIN[Judge Itineraries<br/>autogenerated]
    end

    HR -- "Working patterns,<br/>contractual days<br/>(manual reference)" --> RSU
    EL -- "Judge profiles,<br/>roles, locations<br/>(manual copy)" --> RSU
    RSU -- "Manual data entry<br/>via JI UI" --> MJ
    MJ --> WP
    WP -- "Auto-generates" --> ITIN
-->


**Gap:** There is no automated synchronisation. Users must manually keep both eLinks and JI updated. The training documentation notes this will be revisited once the Judicial Database replacement is complete.

---

## Flow 2 -- Planned Activity Capture (Listing Systems -> JI)

Data on how judges plan to spend their working day is sourced from court listing systems and entered into JI manually. There is no direct integration with case management systems (CaseMan, FamilyMan, Common Platform).

| Attribute | Detail |
|-----------|--------|
| **Source** | Court listing systems |
| **Destination** | JI (Sittings, Judge Itinerary screens) |
| **Data** | Planned sittings, work types (Crime, Civil, Family, S9, Off Circuit), session durations (full day / half day AM/PM), sitting locations |
| **Mechanism** | Manual copy from listing systems into JI by HMCTS court staff. Ad-hoc sittings can also be created directly in JI. |
| **Frequency** | Daily (progressive entry recommended) |
| **Users involved** | Court (Full Access), Regional (Full Access) |
| **Criticality** | Medium -- feeds into utilisation reporting once confirmed |

![Flow 2 — Court listing systems are manually referenced by court staff who enter planned activity into JI's Sittings screen, feeding the Judge and Court itineraries](flow-2-planned-activity-capture.png)

<!--
Diagram source (Mermaid). Regenerate flow-2-planned-activity-capture.png with:
  mmdc -i flow-2-planned-activity-capture.mmd -o flow-2-planned-activity-capture.png -b white -s 3
Use <br/> for label line breaks (Mermaid renders a literal \n as text).

flowchart LR
    subgraph Court Systems
        LS[Listing Systems<br/>e.g. CaseMan,<br/>FamilyMan, CP]
    end

    subgraph Users
        CS[Court Staff]
    end

    subgraph JI
        SIT[Sittings Screen]
        JI_IT[Judge Itinerary]
        CI[Court Itinerary]
    end

    LS -- "Planned activity<br/>(manual reference,<br/>no system link)" --> CS
    CS -- "Manual entry<br/>via JI UI" --> SIT
    SIT --> JI_IT
    SIT --> CI
-->


**Gap:** No system-to-system integration exists. The documentation explicitly states no direct integration with CaseMan, FamilyMan, or Common Platform.

---

## Flow 3 -- Sitting & Booking Confirmation (Court Staff -> JI)

After a sitting or fee-paid booking occurs, court staff confirm it in JI -- verifying that it took place, recording the actual work type, and adjusting the session duration if needed. Confirmed data drives both payment processing and MI reporting.

| Attribute | Detail |
|-----------|--------|
| **Source** | Court staff (local knowledge of what actually happened) |
| **Destination** | JI (Sittings, Fee-paid Bookings screens) |
| **Data** | Confirmation status (confirmed / cancelled / rejected), actual work type, actual session duration, verifier sign-off (County Courts) |
| **Mechanism** | Manual entry via JI UI. Sittings can be confirmed individually or in bulk. County Courts have an additional verification step by a senior manager. |
| **Frequency** | Daily (strongly recommended), at minimum before monthly verification deadline |
| **Users involved** | Court (Full Access), Court (Enhanced CJ), Regional (Verifier) |
| **Criticality** | High -- unconfirmed bookings cannot be exported for payment; unconfirmed sittings are excluded from MI |

![Flow 3 — Court staff confirm fee-paid bookings and salaried sittings in JI; confirmed data flows to payment export and MI reports, with a County Courts verification step](flow-3-sitting-booking-confirmation.png)

<!--
Diagram source (Mermaid). Regenerate flow-3-sitting-booking-confirmation.png with:
  mmdc -i flow-3-sitting-booking-confirmation.mmd -o flow-3-sitting-booking-confirmation.png -b white -s 3
Use <br/> for label line breaks (Mermaid renders a literal \n as text).

flowchart LR
    subgraph Court
        CS[Court Staff]
        VER[Verifier<br/>County Courts only]
    end

    subgraph JI
        FPB[Fee-paid Bookings<br/>Awaiting Confirmation]
        SAL[Salaried Sittings<br/>Awaiting Confirmation]
        CONF[Confirmed<br/>Bookings / Sittings]
        VERIF[Verified Data<br/>read-only, published]
    end

    subgraph Downstream
        PAY[Payment Export]
        MI[MI Reports]
    end

    CS -- "Confirm booking:<br/>actual work type,<br/>session duration" --> FPB
    CS -- "Confirm sitting:<br/>actual work type<br/>(County Courts)" --> SAL
    FPB -- "Confirmed" --> CONF
    SAL -- "Confirmed" --> CONF
    VER -- "Verify month<br/>(County Courts)" --> VERIF
    CONF --> PAY
    CONF --> MI
    VERIF --> MI
-->


**Note:** Accuracy of confirmation directly affects payment correctness. The training documentation emphasises that "the accuracy of the payment schedules sent to Liberata is highly dependent on the checking that goes on here."

---

## Flow 4 -- Absence & Vacancy Management (Courts / RSU -> JI)

Absence recording triggers a multi-step workflow involving court staff, RSU judicial teams, and vacancy/booking management. This is an internal JI workflow with human actors at each step.

| Attribute | Detail |
|-----------|--------|
| **Actors** | Court staff (requesters), RSU / Judicial Team (approvers), Court staff (vacancy decision) |
| **System** | JI (Absences, Vacancies, Fee-paid Bookings screens) |
| **Data** | Absence type, dates, NTBF status, vacancy requirements, fee-paid judge allocations, booking confirmations |
| **Mechanism** | Multi-step approval workflow within JI UI. Email notifications at each stage. |
| **Frequency** | Event-driven |
| **Criticality** | High -- drives vacancy creation, fee-paid bookings, and downstream payments |

![Flow 4 — Absence request workflow: court staff or RSU raise an absence; RSU approval and a fee-paid-cover decision branch into vacancy creation and booking or NTBF, updating itineraries and the payment flow](flow-4-absence-vacancy-management.png)

<!--
Diagram source (Mermaid). Regenerate flow-4-absence-vacancy-management.png with:
  mmdc -i flow-4-absence-vacancy-management.mmd -o flow-4-absence-vacancy-management.png -b white -s 3
Use <br/> for label line breaks (Mermaid renders a literal \n as text).

flowchart TD
    subgraph Court
        CS[Court Staff]
    end

    subgraph RSU
        JT[Judicial Team<br/>RSU]
    end

    subgraph JI Workflow
        ABS[Absence Request<br/>created]
        APPROVE{RSU Approves?}
        REJECT[Absence Rejected]
        COVER{Needs<br/>Fee-paid Cover?}
        NTBF[Marked NTBF<br/>No vacancy created]
        VAC[Vacancy Created]
        BOOK[Fee-paid Judge<br/>Booked]
    end

    subgraph Downstream
        ITIN[Itineraries Updated]
        PAY[Payment Flow<br/>when confirmed]
    end

    CS -- "Request absence" --> ABS
    JT -- "Also can create<br/>directly" --> ABS
    ABS --> APPROVE
    APPROVE -- "Yes" --> COVER
    APPROVE -- "No" --> REJECT
    COVER -- "Yes" --> VAC
    COVER -- "No / NTBF" --> NTBF
    VAC -- "RSU allocates<br/>fee-paid judge" --> BOOK
    BOOK --> ITIN
    NTBF --> ITIN
    BOOK --> PAY
-->


---

## Flow 5 -- Fee-Paid Payment Export (JI -> JFEPS -> Liberata)

This is the most operationally critical integration flow. JI generates payment files from confirmed fee-paid bookings and routes them through a human approval chain to the finance system and payment processor.

| Attribute | Detail |
|-----------|--------|
| **Source** | JI (Payments screen) |
| **Destinations** | JFEPS (finance system), Liberata (payment processor) |
| **Data** | Judge details, payroll numbers, court codes, sitting dates, session types (full/half day), booking IDs, work types, fee amounts, London weighting |
| **Format** | JFEPS-compatible Excel file |
| **Mechanism** | JI validates data (dates, court codes, booking IDs) -> generates Excel -> emails to Payment Authoriser -> authoriser reviews and forwards to Liberata -> authoriser uploads to JFEPS |
| **Frequency** | Weekly |
| **Users involved** | RSU / Judicial Team (generates schedule), Payment Authoriser (reviews and forwards) |
| **Criticality** | Critical -- Crown Courts rely on this as the only mechanism to pay fee-paid judges without manual individual payments |

![Flow 5 — Confirmed fee-paid bookings are validated and turned into a JFEPS-compatible Excel schedule, emailed to a Payment Authoriser who uploads to JFEPS and forwards to Liberata for payment](flow-5-fee-paid-payment-export.png)

<!--
Diagram source (Mermaid). Regenerate flow-5-fee-paid-payment-export.png with:
  mmdc -i flow-5-fee-paid-payment-export.mmd -o flow-5-fee-paid-payment-export.png -b white -s 3
Use <br/> for label line breaks (Mermaid renders a literal \n as text).

flowchart LR
    subgraph JI
        CONF[Confirmed<br/>Fee-paid Bookings]
        VAL[Data Validation<br/>dates, court codes,<br/>booking IDs]
        GEN[Generate Payment<br/>Schedule]
    end

    subgraph Human Review
        PA[Payment Authoriser]
    end

    subgraph Finance
        JFEPS[JFEPS<br/>Finance System]
        LIB[Liberata<br/>Payment Processor]
    end

    subgraph Output
        PAID[Fee-paid Judge<br/>Receives Payment]
    end

    CONF --> VAL
    VAL --> GEN
    GEN -- "JFEPS-compatible<br/>Excel file<br/>via email" --> PA
    PA -- "Reviews, approves,<br/>uploads" --> JFEPS
    PA -- "Forwards<br/>payment schedule<br/>via email" --> LIB
    LIB -- "Processes<br/>payment" --> PAID
-->


**Note:** JI does not hold bank details or process payments directly. Sensitive financial data remains in JFEPS and Liberata. Double-submission is prevented by tracking which bookings have been exported.

---

## Flow 6 -- Payment Reconciliation (JFEPS -> JI)

After payments are processed, finance users reconcile the results back into JI to track which payments succeeded, which are pending, and flag discrepancies.

| Attribute | Detail |
|-----------|--------|
| **Source** | JFEPS / Finance System (payment confirmations) |
| **Destination** | JI (Payment Reconciliation screen) |
| **Data** | Payment status (paid / pending / queried), reconciliation notes, discrepancy flags |
| **Mechanism** | Finance users manually check JFEPS payment confirmations, then flag payments as reconciled in JI. No automated data feed from JFEPS back to JI. |
| **Frequency** | Ongoing as payments are processed |
| **Users involved** | Finance / Payment Authoriser |
| **Criticality** | Medium -- prevents double-payment and surfaces discrepancies |

![Flow 6 — JFEPS payment confirmations reach finance users out-of-band; they manually flag payments as reconciled in JI's Payment Reconciliation screen, updating booking payment status](flow-6-payment-reconciliation.png)

<!--
Diagram source (Mermaid). Regenerate flow-6-payment-reconciliation.png with:
  mmdc -i flow-6-payment-reconciliation.mmd -o flow-6-payment-reconciliation.png -b white -s 3
Use <br/> for label line breaks (Mermaid renders a literal \n as text).

flowchart LR
    subgraph Finance
        JFEPS[JFEPS<br/>Payment Confirmations]
    end

    subgraph Users
        FIN[Finance User /<br/>Payment Authoriser]
    end

    subgraph JI
        REC[Payment<br/>Reconciliation Screen]
        STATUS[Booking Payment<br/>Status Updated]
    end

    JFEPS -- "Payment confirmation<br/>(out-of-band,<br/>not automated)" --> FIN
    FIN -- "Manually flags<br/>as reconciled<br/>in JI" --> REC
    REC --> STATUS
-->


**Gap:** Reconciliation is entirely manual. There is no automated feed from JFEPS back into JI. Finance users must cross-reference two systems.

---

## Flow 7 -- Management Information & Reporting (JI -> DA&I)

JI is the primary source of sitting day data for Civil, Family, and Crown Courts. DA&I extracts this data for management information, performance reporting, and strategic decision-making.

| Attribute | Detail |
|-----------|--------|
| **Source** | JI (Reports screens) |
| **Destination** | DA&I team systems, senior leadership, ministers |
| **Data** | Sitting day summaries, judicial utilisation, vacancy analysis, booking analysis, absence/official business analysis, jurisdictional splits, work type distributions |
| **Format** | Excel and PDF exports from JI report screens |
| **Mechanism** | Export-based -- users run reports in JI, copy/paste or download to Excel/PDF. DA&I then transforms and aggregates. Manual extraction via spreadsheets also used. |
| **Frequency** | Aligned to reporting cycles (monthly, quarterly, annual) |
| **Users involved** | MI / Reporting Users, DA&I analysts |
| **Criticality** | High -- ministers require performance reporting across jurisdictions; JI is the primary data source for courts |

![Flow 7 — JI report screens export sitting, booking, absence and vacancy data as Excel/PDF; DA&I transforms and aggregates it into management information for leadership, ministers and performance teams](flow-7-mi-reporting.png)

<!--
Diagram source (Mermaid). Regenerate flow-7-mi-reporting.png with:
  mmdc -i flow-7-mi-reporting.mmd -o flow-7-mi-reporting.png -b white -s 3
Use <br/> for label line breaks (Mermaid renders a literal \n as text).

flowchart LR
    subgraph JI
        DATA[(Confirmed Sittings,<br/>Bookings, Absences,<br/>Vacancies)]
        RPT[Reports Screens<br/>Sitting analysis,<br/>Vacancy analysis,<br/>Utilisation reports]
    end

    subgraph Export
        XLS[Excel Export<br/>copy-paste / download]
        PDF[PDF Export]
    end

    subgraph DA&I
        ETL[DA&I<br/>Transform & Aggregate]
        MI[Management<br/>Information<br/>Outputs]
    end

    subgraph Consumers
        LEAD[Senior Leadership]
        MIN[Ministers]
        PERF[Performance Teams]
    end

    DATA --> RPT
    RPT --> XLS
    RPT --> PDF
    XLS --> ETL
    PDF --> ETL
    ETL --> MI
    MI --> LEAD
    MI --> MIN
    MI --> PERF
-->


**Gap:** Tribunals data is not captured in JI. Tribunal sitting data is collected manually via spreadsheets managed by different Chamber Presidents' Offices, leaving a significant gap in cross-jurisdictional reporting.

---

## Flow 8 -- Notifications & Communications (JI -> HMCTS Email)

JI uses HMCTS email infrastructure as a transport layer for operational notifications, itinerary distribution, and payment file delivery.

| Attribute | Detail |
|-----------|--------|
| **Source** | JI (various screens) |
| **Destination** | HMCTS email infrastructure -> judges, court staff, RSU, Payment Authorisers |
| **Data** | See trigger table below |
| **Mechanism** | Automated email from JI. Some emails are sent immediately on action; others (e.g. booking acknowledgements) are batched via an overnight process. |
| **Frequency** | Event-driven |
| **Criticality** | High -- operational communications depend on email delivery |

**Email triggers:**

| Trigger Event | Recipients | Content |
|---------------|-----------|---------|
| Booking created | Fee-paid judge | Booking confirmation with dates, court, work type |
| Booking cancelled / rejected | Impacted judge and court staff | Cancellation notification |
| Absence confirmed | Judge | Absence acknowledgement |
| Itinerary updated | Judge and relevant staff | Updated itinerary |
| Payment schedule generated | Payment Authoriser | JFEPS-compatible Excel file attached |
| Sitting/booking changes | Court staff | Alerts within system and optionally via email |

![Flow 8 — JI events (bookings, absences, itinerary updates, payment schedules) drive an email engine that sends via HMCTS email infrastructure to judges, court staff, payment authorisers and RSU](flow-8-notifications.png)

<!--
Diagram source (Mermaid). Regenerate flow-8-notifications.png with:
  mmdc -i flow-8-notifications.mmd -o flow-8-notifications.png -b white -s 3
Use <br/> for label line breaks (Mermaid renders a literal \n as text).

flowchart LR
    subgraph JI Events
        BK[Booking<br/>Created / Cancelled]
        AB[Absence<br/>Confirmed]
        IT[Itinerary<br/>Updated]
        PS[Payment Schedule<br/>Generated]
    end

    subgraph JI
        EM[Email Engine<br/>immediate + overnight batch]
    end

    subgraph HMCTS Email
        SMTP[HMCTS Email<br/>Infrastructure]
    end

    subgraph Recipients
        JDG[Judges]
        CST[Court Staff]
        PA[Payment<br/>Authorisers]
        RSU[RSU / Judicial<br/>Team]
    end

    BK --> EM
    AB --> EM
    IT --> EM
    PS --> EM
    EM --> SMTP
    SMTP --> JDG
    SMTP --> CST
    SMTP --> PA
    SMTP --> RSU
-->


---

## Key Observations

1. **No API integrations exist.** Every integration is either manual data entry, file-based export (Excel/PDF), or email. This limits automation and introduces data quality risks from manual transcription.

2. **The payment flow is the most critical end-to-end integration.** It spans four steps (confirmation -> export -> authorisation -> payment) with human checkpoints at each stage. Any delay in court confirmation cascades into delayed payments.

3. **eLinks integration is aspirational, not operational.** The SRS records it as a non-functional requirement, but no automated data exchange is implemented today.

4. **Reconciliation has no return feed.** Payment outcomes from JFEPS are not automatically reflected in JI. Finance users must manually bridge the two systems.

5. **Tribunals are a blind spot.** JI has no integration with Tribunal listing or scheduling systems. Extending coverage to Tribunals (Employment, Immigration & Asylum, SSCS) is a stated strategic priority.

6. **Future integration pressure.** The Actuals programme and Scheduling & Listing (S&L) reforms both require JI data. The current export-only model will not scale to support these needs.

---

## Source Documents

This analysis is based on the following input documents:

- High Level Capabilities JI.docx
- JI Functional and Non Functional Requirements.docx
- Judicial Itineraries High Level Requirements.docx
- Judicial Itinerary KB.docx
- OPT JI Training Brief DRAFT 02.doc
- UCD resource request.docx
