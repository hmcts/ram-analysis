# SSCS Venue-to-Region — Discovery Questions

| Field | Detail |
|---|---|
| **Purpose** | Reference question set for a discovery session with SSCS operational teams |
| **Topic** | How SSCS hearing venues (centres) map to regions, how JOHs are allocated, and which systems hold the truth |
| **Audience** | SSCS operational / listing / scheduling staff, RSU judicial team, finance/payments |
| **Prepared** | 2026-06-26 |

## 1. Why we are asking

The eLinks Judicial Office reference data gives us SSCS only at **region** level. SSCS sits under the **First-tier Tribunal → Social Entitlement Chamber**, and that chamber has just **9 regional children** (London, Midlands, North East, North West, Scotland, South East, South West, Wales, plus a retired *Unassigned*). There is **no individual centre/venue below region** in that data, and the reference note is explicit that the appointment location "does not necessarily relate to where the JOH is working."

The individual venue only appears at the **sitting** level. In the tribunal sittings/payment export, each sitting carries a free-text `Hearing Venue` tag (e.g. *"AST Anchorage House"*) against a named JOH and date — so venue is a **per-sitting operational fact**, not a standing JOH attribute, and it is not sourced from eLinks.

To build an accurate **venue → region** map we therefore need the operational teams to tell us what the real venue list is, who owns it, and how allocation works in practice. This document is the question set for that session.

**What we already know (state back to confirm, don't re-ask):**

- SSCS = Social Entitlement Chamber of the First-tier Tribunal.
- eLinks holds JOH → chamber → region (9 regions); venue is absent from eLinks.
- Venue shows up only on sitting/payment records as a free-text tag.
- Scheduling currently runs on ListAssist (Cardiff) and other legacy systems across the SSCS regions.

## 2. Venue inventory & definitions

- What is the authoritative, complete list of SSCS hearing venues currently in use?
- What counts as a "venue" for SSCS — a physical hearing centre, an administrative office, a paper/remote channel, or all of these?
- Are remote/video and paper (on-the-papers) hearings treated as venues, or handled separately? If separately, how?
- Does each venue have a stable code/identifier, or is it only ever referred to by name (as the free-text `Hearing Venue` tag suggests)?
- How are new venues added or old ones closed, and who authorises that?
- Are there venues shared with other chambers or jurisdictions (e.g. shared HMCTS hearing centres)? How is that handled?

## 3. Venue → region mapping

- Does a defined venue-to-region mapping exist today, and if so where is it held (system, spreadsheet, local knowledge)?
- Do the 9 SEC regions we see in eLinks match the regions operational teams actually use, or do you work to a different regional model?
- Is the mapping strictly one venue → one region, or can a venue belong to more than one region?
- Are there venues that are national or region-agnostic (we see a "National" placeholder in the data)? How should those be treated?
- How stable is the mapping — does a venue ever move between regions, and what triggers that?
- Who is the owner / maintainer of this mapping, and how often is it reviewed?

## 4. JOH allocation in practice

- When a JOH is allocated, are they allocated to a **region**, to **specific venues**, or to both?
- Can a single JOH sit across multiple venues — and across multiple regions? How common is that?
- How is the venue for a given sitting actually decided — by the listing team, by the JOH's preference, by case location, by rota?
- Is there a concept of a JOH's "home" or "base" venue distinct from where they sit?
- Are fee-paid and salaried JOHs allocated differently with respect to venue/region?
- How are travel, expenses and "London weighting"-type factors affected by venue vs region?

## 5. Systems & data sources

- Which system is the **source of truth** for the venue of an SSCS sitting today?
- Across the SSCS regions, which scheduling/listing tools are in use (ListAssist for Cardiff — what do the other regions use)?
- Where does the venue value originate before it reaches the sittings/payment export — is it keyed manually, or pulled from a listing/case system?
- Is venue ever reconciled back against a master venue list, or is the free-text tag the only record?
- How do venue, the case-management/listing system, and eLinks relate — does any system already join JOH → venue → region?
- Is there a venue reference dataset anywhere (even a maintained spreadsheet) we could take as a starting point?

## 6. Process & workflow

- Walk us through, end to end, how a JOH ends up scheduled at a specific venue on a specific date.
- Who performs venue allocation, and at what point in the scheduling cycle?
- How is venue capacity / room availability factored in, and where is that information held?
- What happens when a sitting is moved to a different venue after it has been scheduled — how is the change recorded?
- How is the venue captured for payment purposes, and does the payment venue always match the listed venue?

## 7. Data quality & edge cases

- We see `Unassigned` (retired) and `National` placeholder locations in the reference data — what do these mean operationally, and are equivalents used for venues?
- How are sittings handled where the venue is unknown, ad-hoc, or not yet confirmed?
- Are there inconsistencies in venue naming (abbreviations, duplicates, spelling variants) we should expect when matching the free-text tags?
- How far back is venue data reliable, and have venue names/regions been re-organised historically (e.g. the move from the predecessor CIPHR system)?
- Are there SSCS-specific venue types (e.g. Asylum Support "AST" venues) that follow different rules from mainstream SSCS hearings?

## 8. Future state (RAM Pathfinder implications)

- If RAM Pathfinder is to schedule at venue granularity, where should the authoritative venue list live, and who should own it?
- Would the operational teams want venue allocation to remain region-led, or move to explicit venue-level allocation?
- What would "good" look like for a venue → region reference dataset that RAM could consume or maintain?
- Are there upcoming changes to SSCS venues, regions, or listing systems we should design around?
- Who must sign off a venue/region model before it can be used for scheduling?

## 9. Artefacts to request in (or after) the session

- The current authoritative SSCS venue list (any format).
- Any existing venue → region mapping (system extract or spreadsheet).
- A sample of recent sitting/listing records showing venue, region, JOH and date.
- Names of the scheduling/listing systems per region and their owners.
- Any local working documents or rotas used to allocate JOHs to venues.

> Context sources: eLinks Pivotal reference-data export 2026-06-01 (Social Entitlement Chamber region structure); tribunal sittings/payment template (`Hearing Venue` tag); Judicial Office *Locations* reference note.
