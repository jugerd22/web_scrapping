

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin


# Tor SOCKS proxy configuration
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}
base_url = 'https://reycdxyc24gf7jrnwutzdn3smmweizedy7uojsa7ols6sflwu25ijoyd.onion'
archive_url = urljoin(base_url, "/archives/")

def get_page(url):
    return requests.get(url, proxies=proxies, headers={"User-Agent": "Mozilla/5.0"})

response = get_page(archive_url)

if response.status_code == 200:
    print("Tor connection")
else:
    print("No Tor connection")

soup = BeautifulSoup(response.text, 'html.parser')

blog_posts = []

def extract_information(page_to_extract):
    title = page_to_extract.find("h1", class_="posttitle p-name").string.strip()

    posted_at = page_to_extract.find("time", class_="dt-published").string.strip()

    category = page_to_extract.find("a", class_="category-link").string.strip()

    author = page_to_extract.find("span", class_="p-name").string.strip()

    content = page_to_extract.find("div", class_="content e-content").text

    blog_posts.append({
        'title': title,
        'posted_at': posted_at,
        'category': category,
        'author': author,
        'content': content,
    })

def next_page(page_to_get):
    next_page_href = page_to_get.find("div", class_ = "pagination").find("a").get("href")
    if next_page_href is None:
        return None

    next_page_full_url = urljoin(base_url, next_page_href)
    response_page = get_page(next_page_full_url)
    return BeautifulSoup(response_page.content, 'html.parser')

def extract_from_list(list_page):
    for post in list_page.find_all("li", class_ = "post-item"):

        relative_url =  post.find("span").find("a").get("href")

        page_full_url = urljoin(base_url, relative_url)

        response_page = requests.get(page_full_url, proxies=proxies, headers={"User-Agent": "Mozilla/5.0"})

        page_soup = BeautifulSoup(response_page.content, 'html.parser')

        extract_information(page_soup)

extract_from_list(soup)
page = next_page(soup)
nb_pages = 0

while page is not None:
    extract_from_list(page)
    page = next_page(page)
    nb_pages = nb_pages + 1
    print(nb_pages)
    print(blog_posts)

with open("blog_posts.json", "w", encoding="utf-8") as f:
    json.dump(blog_posts, f, ensure_ascii=False, indent=4)

