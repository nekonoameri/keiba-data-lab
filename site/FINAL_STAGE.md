# v13 final-stage implementation

## One-command update

```bash
pip install -r requirements.txt
python update_site.py --fetch --year 2026
```

This downloads only annual-results PDFs linked by the official JRA annual-results page, parses them, imports SQLite, validates the DB, rebuilds aggregates and regenerates real race/date pages.

## Official popularity enrichment
PDF extraction intentionally leaves `popularity` blank when it cannot be verified. To enrich it from official JRA race-result HTML, put official result URLs in `official_result_urls.txt` (one per line), then:

```bash
python update_site.py --year 2026 --result-urls official_result_urls.txt
```

The HTML adapter updates official popularity, jockey, finish, horse number/name and source URL. It rejects non-JRA hosts and does not guess opaque JRA URL suffixes.

## Production SEO files
After deciding the domain:

```bash
python build_sitemap.py --base-url https://YOUR-DOMAIN.example
```

This creates `sitemap.xml` and `robots.txt` from actual generated HTML pages.

## Data integrity
`validate_data.py` fails the build on impossible race numbers/distances, invalid horse numbers/popularity, duplicate races, or orphan runners.

## Recommended production schedule
Run once after JRA publishes the day's annual-results PDFs. The official 2026 page states PDFs are published the day after the meeting. Do not hammer the source; the included fetcher is sequential and defaults to a one-second delay.

## Remaining deployment-only items
1. Choose domain/hosting.
2. Set the real domain and build sitemap.
3. Configure a daily/meeting-day scheduled run on the host.
4. Add analytics/ads only after pages contain verified data and privacy/consent pages are prepared.
5. Keep source adapters replaceable; do not couple the UI to one acquisition source.
