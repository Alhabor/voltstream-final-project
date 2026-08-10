# Background Research: EV Charger Data Intake

Last reviewed: 2026-08-09

## Research question

Is heterogeneous EV-charger intake a real and defensible problem for a guarded
generative-AI prototype, and what can public evidence support without claiming
access to Con Edison internal data?

## Findings

### 1. Heterogeneous collection is present in a major public EV dataset

The U.S. Department of Energy Alternative Fuels Data Center (AFDC) says its
Station Locator receives EV charging-station data through three distinct
methods: daily API imports for connected networks, periodic spreadsheet/CSV
imports for networks without an API connection, and manual entry for
non-networked stations. AFDC recommends OCPI for networks using an API.

This is useful evidence that EV charging data can arrive through materially
different ingestion paths. It does **not** prove that Con Edison uses the same
pipeline or has the same errors.

**Presentation-ready surprising fact:** A national public charging-station
directory is not fed by one uniform stream; it combines daily APIs, periodic
spreadsheets, and manually maintained records.

Source: [DOE AFDC — Electric Vehicle Charging Networks](https://afdc.energy.gov/stations/charging-networks)

### 2. Public station data exposes a broad, structured field surface

The official Alternative Fuel Stations API returns station data in JSON, CSV,
or GeoJSON and exposes fields relevant to this prototype, including location,
status, EVSE counts, network, connector types, identifiers, and update dates.
This makes AFDC an appropriate public reference for field concepts and for
creating clearly labeled synthetic variations.

The prototype should not copy the complete API schema. A compact schema is
needed so every test field can be hand-labeled and explained.

Source: [NREL Developer Network — All Stations API](https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/all/)

### 3. Con Edison publicly documents a multi-party submission workflow

Con Edison's PowerReady page describes an application and engineering-review
process involving applicants, approved contractors, uploaded project
documents, Con Edison engineers, construction verification, and closeout
documentation. This supports the business plausibility of an intake checkpoint
between external submissions and internal review.

The page does not establish the precise data-quality failure rate or the
internal systems used by Con Edison. The prototype must not make either claim.

Source: [Con Edison — PowerReady Light-Duty Vehicle Program](https://www.coned.com/en/our-energy-future/electric-vehicles/power-ready-program)

### 4. New York's Make-Ready program has formal reporting obligations

The New York Public Service Commission's public docket identifies Case
18-E-0138 and the July 16, 2020 order establishing the Electric Vehicle
Infrastructure Make-Ready Program and other programs. This is the primary
regulatory record for the program context.

Source: [NYSDPS Document and Matter Management — Case 18-E-0138 filing](https://documents.dps.ny.gov/public/MatterManagement/MatterFilingItem.aspx?FilingSeq=249404&MatterSeq=56005)

### 5. Joint Utilities have publicly described reporting difficulties

A Joint Utilities presentation filed on the NYSDPS document system states that
data collection and reporting are used to assess program costs, performance,
station use and uptime, and grid impacts. It also reports observed challenges
obtaining complete data from participants and EVSE network providers. The
listed reporting categories include program participation, utility system and
billing information, plug/session data, and financial information.

The presentation is marked “for discussion purposes only — subject to change.”
It is evidence of reported challenges at that time, not a current audited
performance measure. This project therefore uses its qualitative finding and
does not repeat its point-in-time counts as current facts.

Source: [NYSDPS-hosted Joint Utilities presentation — Make-Ready reporting overview](https://documents.dps.ny.gov/public/Common/ViewDoc.aspx?DocRefId=%7B346CBF89-A0E8-43B6-8CCC-4C7B35222B7C%7D&DocTitle=Joint+Utilities+Presentation)

## What the evidence supports

- EV-charger information is collected through heterogeneous technical paths in
  at least one authoritative national dataset.
- Public Con Edison program material describes documents moving from external
  applicants/contractors into engineering and verification steps.
- New York program materials identify meaningful reporting obligations and
  publicly reported data-availability/completeness challenges.
- A narrow intake gatekeeper is therefore a reasonable prototype to test.

## What the evidence does not support

- A measured error rate, labor cost, or processing delay inside Con Edison.
- A claim that the public AFDC schema equals Con Edison's internal schema.
- A claim that an LLM improves quality, cost, or speed before experiments run.
- A claim that this prototype satisfies PSC reporting requirements.
- A recommendation for production deployment.

## Data and publication boundary

Evaluation inputs will be public or synthetic. Synthetic records may borrow
field concepts from AFDC, but they must be labeled as constructed evaluation
cases rather than real Con Edison records. No private operational data, personal
data, customer account data, credentials, or confidential contractor material
belongs in the repository or presentation.

## Model-source note for the evaluation

DeepSeek's official API documentation currently lists the available model IDs,
versions, features, and per-token prices. Those facts should be captured with a
run timestamp because the provider says prices may change. Separately, the
official DeepSeek Hugging Face model card publishes the
`DeepSeek-V4-Flash-0731` checkpoint and states that its repository and model
weights use the MIT License. That supports classifying the V4 Flash family as
open-weights even when it is invoked through a hosted API. The hosted API does
not expose a checkpoint hash, so the run manifest must preserve that limitation
instead of claiming bit-for-bit identity with the downloadable checkpoint.

Neither source supplies the required closed-model comparison. The team must
name and document a genuinely closed model separately before claiming the
assignment's model-comparison requirement is complete.

Sources: [DeepSeek API models and pricing](https://api-docs.deepseek.com/quick_start/pricing/),
[DeepSeek-V4 official collection](https://huggingface.co/collections/deepseek-ai/deepseek-v4),
and [DeepSeek-V4-Flash-0731 official model card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731)

## Research limitations

- Public program pages and regulatory documents may change after the review
  date; the team should recheck time-sensitive program status before presenting.
- The course brief supplied by Con Edison is the source for the partner-specific
  problem statement. Public sources corroborate context but do not replace it.
- The prototype's value must be determined by the fixed evaluation, not by the
  plausibility of the background story.
