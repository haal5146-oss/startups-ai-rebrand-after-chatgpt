# Data dictionary

## `companies.csv`

One row per company on the 2021 Forbes Cloud 100.

| Field | Meaning |
|---|---|
| `rank` | Rank on the 2021 Forbes Cloud 100, 1 to 100 |
| `company` | Company name as Forbes listed it |
| `slug` | Lowercase name used for file names in `cache/` |
| `industry` | Forbes' one-line description of the company's industry |
| `homepage` | The homepage looked up in the Wayback Machine, without `https://` or `www.` |
| `homepage_source` | `forbes` if the homepage came from Forbes' own list data, `added` if Forbes had none (or listed a subpage, as for Canva) and I added the company's main domain |

## `sample_homepages_clean.csv`

One row per company per quarter, Q1 2019 to Q4 2025. The sample has the ten highest-ranked companies; the full file, `homepages_clean.csv`, has all 100 and the same fields.

| Field | Meaning |
|---|---|
| `rank`, `company`, `homepage` | As in `companies.csv` |
| `quarter` | Calendar quarter, such as `2022Q4` |
| `status` | `ok`: page fetched and parsed. `thin_text`: fetched, but under 200 characters of visible text, usually a page built with JavaScript. `no_capture`: the Wayback Machine has no usable capture that quarter. `fetch_failed`: the capture couldn't be downloaded. `not_fetched`: not downloaded yet |
| `capture_date` | Date of the capture that was parsed. When the archived homepage redirected, this is the date of the page it redirected to |
| `final_host` | The site the archived page came from after any redirects, such as `gomotive.com` for KeepTruckin |
| `redirected` | `True` if `final_host` is not the `homepage` looked up, usually because the company changed its domain |
| `html_lang` | The page's declared language, from `<html lang>`. Chinese pages (`zh`) can't be compared word for word |
| `title` | The page's `<title>` |
| `text_chars` | Characters of visible text after scripts, styles and `noscript` blocks are removed |
| `ai_count` | Times `AI` appears as a whole word in capitals |
| `artificial_intelligence_count` | Times "artificial intelligence" appears, any case |
| `machine_learning_count` | Times "machine learning" appears, any case |
| `generative_count` | Times "generative" appears as a whole word, any case |
| `ai_terms_total` | The four counts added up |
| `mentions_ai` | `True` if `ai_terms_total` is more than 0. Empty when there was no usable page, so a missing quarter never counts as "no AI" |
