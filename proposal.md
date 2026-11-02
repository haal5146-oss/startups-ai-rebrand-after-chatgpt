# Did Startups Rebrand as "AI" Companies After ChatGPT?

Haziq Ali · INFO 4617 Final Project Proposal

## 1. Research question

**Question:** How many of the 2021 Forbes Cloud 100 startups added "AI" to their homepages between 2019 and 2025, and did that shift start before or after ChatGPT's public release on November 30, 2022?

I honestly don't know what the answer will look like. The share of homepages mentioning AI could stay flat, creep up slowly from 2019, or spike in a single quarter, and every company has its own "first quarter mentioning AI" that can fall anywhere in the window.

**Who would care:**

- Founders and investors trying to figure out how to pitch a company, and whether "AI" in the pitch is now expected.
- Tech reporters covering the AI boom, who could back up (or knock down) the idea that everyone rebranded, using actual numbers instead of anecdotes.
- Regulators and lawyers keeping an eye on "AI washing," which is when companies overstate how much they actually use AI. The SEC brought its first AI washing cases in 2024, so this is a real concern.
- Researchers who study how hype spreads through an industry.

**What I expect:** My guess is that almost no homepages mention AI before late 2022, most do by the end of 2024, and the biggest jump happens in the two or three quarters right after ChatGPT.

**What would surprise me:** if a big chunk were already saying "AI" back in 2019 to 2021, if the rise didn't show up until 2024 or later, or if some companies added AI and then quietly took it back off.

## 2. Data source and method

**Sources:**

- The Internet Archive's Wayback Machine. The CDX Server API (https://web.archive.org/cdx/search/cdx) lists every capture of a page, and archived pages are fetched at https://web.archive.org/web/[timestamp]id_/[url].
- The company list: the 2021 Forbes Cloud 100. I picked it because it came out before ChatGPT, so the 100 private, venture backed software companies on it weren't chosen for having anything to do with AI. I'll copy the names and homepage URLs into a CSV by hand.

**How I will get it:** Mostly Chapter 7 (Web Archives). I'll use the CDX Server API to find one capture per quarter for each homepage, then download each capture's raw HTML. From there I'll parse the pages with BeautifulSoup (Chapter 6), strip out scripts and styles, and keep just the visible text and the page title. I'll also use Chapter 7's caching setup so every page gets saved to disk and is never requested twice.

**Scope:** 100 company homepages, one capture per quarter from Q1 2019 through Q4 2025 (28 quarters). That's up to 2,800 archived pages plus 100 CDX lookups, collected once, since it's all historical.

**Analysis:**

- For every homepage and quarter, whether the text or title mentions "AI," "artificial intelligence," "machine learning," or "generative," and how many times.
- A line chart showing what share of the 100 companies mention AI each quarter, with a marker at Q4 2022, when ChatGPT came out.
- The first quarter each company mentions AI, so I can count how many switched before versus after ChatGPT.
- A bag of words comparison (from Chapter 7) of the 2021 and 2025 homepages, to see which other words went up or down along with "AI."

## 3. Ethics and feasibility

**Rules for collection:**

- I checked, and web.archive.org doesn't have a robots.txt (the request comes back 404), so there are no crawler rules to follow there. The Internet Archive's Terms of Use allow access for scholarship and research, which is what this is.
- The homepages themselves are public marketing pages. I'm only counting words on them, not republishing them, which should fall under research and fair use.
- To stay within limits, I'll send a User Agent that identifies me ("WebDataScience/1.0 (INFO 4617; haal5146@colorado.edu)"), wait at least 5 seconds between requests, cache every page, and back off whenever the Archive answers 429 Too Many Requests.

**Personal information:** Some homepages have customer testimonials with real people's names and photos. I won't store or report any of that. My dataset will only have the company, the capture date, the page title, and word counts. The raw HTML I cache stays on my laptop so the work can be reproduced, and I won't publish it.

**One record, retrieved:** On October 25, 2026, I tested this on Notion's homepage, comparing January 2022 to July 2025:

Code:

```python
HEADERS = {"User-Agent": "WebDataScience/1.0 (INFO 4617; haal5146@colorado.edu)"}
for ts in ["20220101192139", "20250701"]:
    url = f"https://web.archive.org/web/{ts}id_/https://www.notion.so/"
    r = requests.get(url, headers=HEADERS, timeout=60)
    soup = BeautifulSoup(r.text, "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    text = " ".join(soup.get_text(" ").split())
    print(ts, r.status_code, soup.title.string, len(re.findall(r"\bAI\b|artificial intelligence", text, re.I)))
    time.sleep(5)
```

What came back:

```text
20220101192139 200 Notion 0
20250701 200 The AI workspace that works for you. | Notion 14
```

I also ran a CDX request for notion.so in 2022, which came back with status 200 and one capture per month, with the fields urlkey, timestamp, original, mimetype, statuscode, digest, and length.

**Fields I will use:** from the CDX API, timestamp, original, and statuscode, so I can pick one working capture per quarter. From each page, the title and visible text, which is where I'll count the AI terms.

**Biggest risk and fallback:** The Archive limits how fast you can make requests. My very first test got a 429 Too Many Requests, and some homepages are built with JavaScript or have gaps where a quarter was never captured. If collection ends up too slow or too patchy, I'll cut it down to 30 companies with one capture per year (7 each, about 210 pages), and mark quarters with no usable capture as missing instead of counting them as "no AI."

## AI tools

I used AI to find sources, and then had it formalize my proposal to have it read more clean and structured. I understand the question, the source, and the method, and I can explain all of them myself.
