# Did Startups Rebrand as "AI" Companies After ChatGPT?

**Haziq Ali** · INFO 4617 Final Project

## Summary

How many of the 2021 Forbes Cloud 100 startups added "AI" to their homepages between 2019 and 2025, and did that shift start before or after ChatGPT's public release on November 30, 2022? This project uses the Internet Archive's Wayback Machine to collect one capture per quarter of each company's homepage, then counts mentions of AI terms in the page text and title. The 2021 list came out before ChatGPT, so these companies weren't chosen for having anything to do with AI, which makes it possible to see whether the rebrand was already underway or followed ChatGPT.

## Data

**Source.** The company list is the 2021 Forbes Cloud 100, taken from Forbes' own list data (`forbesapi/org/cloud100/2021`) as the Wayback Machine archived it on August 10, 2021. Forbes gave a website for 52 of the 100 companies; I added the other 48 by hand, checked each against the archive, and marked them in `data/companies.csv`. The homepages come from the Internet Archive's Wayback Machine: the CDX Server API lists each homepage's captures, and each chosen capture is downloaded raw, through its `id_` address.

**When.** Collected on November 8, 2026, starting at 19:39 UTC. Every request sends a User-Agent that identifies me and waits 5 seconds after it.

**How many records.** 100 companies × 28 quarters (Q1 2019 to Q4 2025) = 2,800 company-quarters. 2,683 of them have a capture in the archive; 117 don't, mostly because the Internet Archive refuses requests for three of the sites (Toast, Klaviyo and Miro, status 403) and because Loom's later domain is blocked too. Collection runs in two passes: Q4 of every year first, then the other quarters. `analysis.ipynb` prints how many pages had been fetched when it last ran.

**What the repository holds.** `data/companies.csv` (all 100 companies), `data/sample_homepages_clean.csv` (every quarter for the ten highest-ranked companies) and `data/data_dictionary.md` (every field and what it means).

**What I kept out, and why.**

- **The raw HTML** (`cache/`). The homepages are the companies' copyrighted marketing pages, some show customer testimonials with real people's names and photos, and the full set is thousands of files. My proposal promised it would stay on my laptop. `collect.py` downloads it again.
- **The full cleaned file** (`data/homepages_clean.csv`). The repository has a sample, as the assignment asks, and `analysis.ipynb` rebuilds the full file from the cache.

**Known issues.** Some captures are pages built with JavaScript that have almost no text, such as Notion's in 2019; they are marked `thin_text` instead of counted as "no AI". Two companies' homepages are in Chinese (FanRuan and Jushuitan), and the archive caught Canva's homepage in German in 2019, so English word counts undercount them.

## Methods

Coming soon.

## Findings

Coming soon.

## How to reproduce

Coming soon.
