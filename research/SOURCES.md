# Source Register

Last link check: 2026-08-09

Only authoritative primary sources are used for factual background. Access
dates are included because program pages and live data documentation can change.

| ID | Publisher | Title and link | Accessed | Used for | Caveat |
|---|---|---|---|---|---|
| S1 | U.S. Department of Energy, Alternative Fuels Data Center | [Electric Vehicle Charging Networks](https://afdc.energy.gov/stations/charging-networks) | 2026-08-09 | Three collection paths: daily API, periodic CSV, and manual entry; network terminology | Describes AFDC, not Con Edison |
| S2 | National Renewable Energy Laboratory Developer Network | [All Stations API](https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/all/) | 2026-08-09 | Official output formats and public station-field reference | Full API schema is broader than the prototype |
| S3 | Consolidated Edison | [PowerReady Light-Duty Vehicle Program](https://www.coned.com/en/our-energy-future/electric-vehicles/power-ready-program) | 2026-08-09 | Applicant/contractor documents, engineering review, work verification, and closeout workflow | Live program status is time-sensitive; recheck before presentation |
| S4 | New York State Department of Public Service | [Case 18-E-0138 filing: Order Establishing Electric Vehicle Infrastructure Make-Ready Program and Other Programs](https://documents.dps.ny.gov/public/MatterManagement/MatterFilingItem.aspx?FilingSeq=249404&MatterSeq=56005) | 2026-08-09 | Primary regulatory docket, order title, and filing date | Docket context, not proof of prototype compliance |
| S5 | Joint Utilities, hosted by New York State Department of Public Service | [Make-Ready Program reporting overview](https://documents.dps.ny.gov/public/Common/ViewDoc.aspx?DocRefId=%7B346CBF89-A0E8-43B6-8CCC-4C7B35222B7C%7D&DocTitle=Joint+Utilities+Presentation) | 2026-08-09 | Reporting categories and publicly observed data-reporting challenges | Marked for discussion and subject to change; point-in-time figures are not used as current facts |
| S6 | DeepSeek | [Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/) | 2026-08-09 | Current API model identifiers, versions, supported features, token accounting, and published prices | API availability and prices can change; snapshot exact metadata in each run |
| S7 | DeepSeek official Hugging Face organization | [DeepSeek-V4 collection](https://huggingface.co/collections/deepseek-ai/deepseek-v4) and [DeepSeek-V4-Flash-0731 model card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731) | 2026-08-09 | Confirms that the tested Flash checkpoint is published and that its repository and model weights are MIT-licensed | Public weights establish open-weights status; using a hosted API does not make it a closed model |

## Citation rules for repository artifacts

1. Link factual claims directly to the source above.
2. Do not copy changing station or program counts unless the artifact states the
   source date and the count is necessary.
3. Distinguish an official requirement/order from a discussion presentation.
4. Distinguish public AFDC data architecture from Con Edison operations.
5. Label all constructed examples and evaluation cases as synthetic.
6. Recheck S3 and any other live program-status claim immediately before the
   final presentation.
7. For model classification, cite the exact model card/license. Do not infer
   open-weights or closed status from an API provider name.
8. For cost calculations, store token counts and the price-page access date;
   published prices are time-sensitive.

## Source-selection notes

Search results, vendor marketing pages, news summaries, and unsourced blog posts
were not used as evidence. The source list favors DOE/NREL, Con Edison, and New
York State Department of Public Service materials so each claim remains
traceable to an original publisher.
