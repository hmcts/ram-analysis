# Functional Decomposition — JI Legacy Application (As-Is)

A high-level inventory of *what the legacy Judicial Itineraries (JI) application lets a user do* — its functions, not its implementation. It exists to inform the design of the RAM Pathfinder replacement: it fixes the set of capabilities the new system must cover or consciously drop.

| Attribute | Detail |
|---|---|
| Source of truth | Screenshots of the legacy JI application (`ji-input-docs/ji-screenshots/` — 36 screens across Manage JOH, Absences/Vacancies/Bookings, Itinerary, Sittings) |
| Method | Each function phrased as *verb + object*; variations collapsed; classified into exactly one domain |
| Scope | Capabilities visible on screen only. No prior knowledge of similar systems was used to add functions. |
| Out of scope | Fields, buttons, screen/tab names, navigation, internal logic, data flows, calculations |

Functions are grouped into six domains: **JOH data management**, **Absence**, **Vacancy**, **Sitting**, **Payment**, **Itinerary management**. The absence → vacancy → booking → payment → reconciliation lifecycle is described in the system's own words on the *Absence, Vacancy and Booking tasks* landing screen, which anchors the domain boundaries below.

## JOH data management

Maintaining records about judicial office holders: profiles, status, ticketing/eligibility, venues, working patterns and targets.

- Search for judicial office holders by location, type and status
- Maintain a JOH's profile and contact details
- Maintain a JOH's side-specific details, tickets and eligibility
- Record a JOH's base location, alternative venues and retirement date
- Maintain a JOH's working pattern and jurisdictional split
- Set a JOH's target sitting days
- View a JOH's sitting and availability statistics
- Export the managed-judge list to Excel

## Absence

Recording and managing a member becoming unavailable, including approval and the decision on whether cover is needed.

- Request an absence for a JOH (by judge or local office)
- Record an Other Business (OB) period for a JOH
- Approve or reject a requested absence
- Indicate whether an approved absence requires fee-paid cover
- View requested and confirmed absences
- Send a notification email when recording an absence

## Vacancy

Managing an unfilled slot once it exists: identifying it, advertising it, and filling it with fee-paid cover.

- Create a vacancy arising from an approved absence
- Create a vacancy not arising from an absence
- Advertise vacancies / maintain the advertising plan
- View outstanding and all vacancies
- Fill a vacancy by booking a fee-paid judge (including cross-region cover)
- Create a filled vacancy and its fee-paid booking in one step
- Cancel a fee-paid booking when cover is no longer required

## Sitting

Planning and running sessions: creating them, allocating members, and confirming what actually happened.

- Create a sitting/session for a salaried judge
- View planned sittings by salaried judges
- Confirm and verify a sitting and record the actual work type set
- Cancel a sitting
- Book an off-circuit judge as a standalone sitting
- Book a High Court judge into the itinerary
- Book a reserved-matter sitting

## Payment

Paying members: clearing sessions for payment, sending payment data to finance, and reconciling it.

- Confirm that a fee-paid judge sat and record the work heard (clear for payment)
- Confirm and send fee payments to finance (LIBERATA), notifying the authoriser
- Reconcile fee payments against the LIBERATA cash report and identify discrepancies

## Itinerary management

Viewing and maintaining itineraries — both court-driven (office) and judge-driven.

- View and update the court (office) itinerary of sittings, bookings, vacancies and unfilled absences
- View and update a JOH's itinerary of sittings and absences
- View a forward look of sittings and absences across judges
- Create an ad-hoc itinerary for a JOH
- Email a JOH their itinerary
- Export an itinerary or report to Excel

## Inferred — needs confirmation

- **Create a new "JOB" for a JOH** — a *Create New JOB* button is visible on the judge's Itinerary tab, alongside *Create Ad Hoc Itinerary*, but the screenshots don't reveal what it produces (judicial office booking? job/sitting record?). Listed here rather than guessing its capability.
- **Automated allocation of members to sessions** — not evidenced. Every sitting creation and booking seen is manual; no auto-allocation or panel-composition screen appears.

## Notes on scope and ambiguity

- The **Reports** and **Admin** top-nav tabs appear on every screen, but no screenshot shows their contents — so no functions are listed for them. (The *Forward Look* report does appear, under Judge Itinerary, and is captured above.)
- **"Send Adj. Email"** — the abbreviation is unconfirmed (adjustment vs adjournment); the function is kept generic as a notification email.
- **Salaried-judge sitting confirmation** (Sitting) and **fee-paid "judge sat" confirmation** (Payment) look similar but are distinct: one verifies the planned salaried sitting and its work type; the other clears a fee-paid booking for payment. They are kept in separate domains.
