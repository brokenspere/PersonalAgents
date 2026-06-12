# Lightweight Scraping with BeautifulSoup

We decided to use `BeautifulSoup` (static HTML parsing) instead of `Playwright` (headless browser) for the initial Yahoo Finance ScraperWorker.

While Playwright provides more robust handling of JavaScript-heavy pages, it requires bundling browser binaries, which significantly increases Docker container size and runtime memory/CPU requirements. Because a key goal is to keep deployment lightweight for future cloud hosting (e.g., AWS), we will attempt to extract the required headlines from static HTML first. We will only transition to Playwright if Yahoo Finance's structure proves impossible to parse statically.