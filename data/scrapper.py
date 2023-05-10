import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path

visited_links = set()
skip_link = "#docusaurus_skipToContent_fallback"


def is_valid(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def build_file_path(parsed_url):
    path = Path(parsed_url.path)

    if path.name == "":
        file_path = path.joinpath("index.html")
    elif not path.suffix:
        file_path = path.with_suffix(".html")
    else:
        file_path = path

    return Path(str(file_path).lstrip('/'))

def save_html(url, content):
    save_directory = "saved_pages"
    parsed_url = urlparse(url)

    file_path = build_file_path(parsed_url)
    save_path = Path(save_directory, parsed_url.netloc, file_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with open(save_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Saved: {save_path}")


def crawl(url, base_url):
    if url in visited_links or not is_valid(url) or not url.startswith(base_url):
        return

    visited_links.add(url)
    print(f"Crawling: {url}")

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Process the current page content as needed
    save_html(url, soup.prettify())

    for link in soup.find_all("a"):
        href = link.get("href")
        if href == skip_link:
            continue

        next_url = urljoin(base_url, href)
        crawl(next_url, base_url)

if __name__ == "__main__":
    start_url = "https://docs.cloud.coinbase.com"
    base_url = "https://docs.cloud.coinbase.com"
    crawl(start_url, base_url)
