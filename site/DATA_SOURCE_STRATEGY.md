# Data source strategy

The ingestion layer must not depend on one PDF parser.

## Priority
1. Structured historical CSV import (bootstrap)
2. HTML race-result adapter for incremental/current results
3. JRA official pages/PDFs for verification and fallback
4. Licensed commercial feed when public redistribution requires it

## Adapter contract
Every source normalizes into races.csv and runners.csv. Source-specific scraping/parsing stays outside analytics and presentation.

## Historical bootstrap candidate
The public Kaggle JRA dataset documents race-result, odds, lap-time and corner-order CSVs covering 1986-01-05 through 2021-07-31. Before publishing derived data, verify the dataset/source licence and redistribution conditions.

## Current-data candidate
Use an HTML result adapter with conservative rate limiting and resumable imports. Do not bypass authentication, access controls, CAPTCHAs, robots restrictions, or contractual restrictions.

## Verification
Cross-check sampled races against JRA official result pages. Never infer official popularity from odds when the source does not provide popularity.

## Release gate
No deployment is considered data-ready unless races > 0, runners > 0, and sampled normalized rows pass validation.
