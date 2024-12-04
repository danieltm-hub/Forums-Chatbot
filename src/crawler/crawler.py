import requests
import os
from queue import Queue
from bs4 import BeautifulSoup

from src.crawler.utils import ForumPage, is_absolute_path

base_url = "https://us.forums.blizzard.com"

def fetch_page(url:str) -> str | None:

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a {url}: {e}")
        return None
    
def parse_page(html:str, page:ForumPage, visited_urls:set) -> list[ForumPage]:
  
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for link in soup.find_all('a', href=True):
        
        url = link['href']
        
        if not is_absolute_path(url):
            url = base_url + url
        
        if url in visited_urls:
            continue

        new_page = ForumPage(url) if not page.is_category() else ForumPage(url, page.main_class, page.sub_class)
        
        if new_page.is_topic() and page.is_just_category():
            continue
        
        visited_urls.add(url)
        
        links.append(new_page)

    return links

def save_html(content:str, page:ForumPage):

    if not page.is_topic():
        return
    
    print(f"Saving {page.url}")

    folder = f"./data/{page.main_class}/{page.sub_class}/"
    filename = "_".join(page.url.split("/")[-2:])

    with open(folder + filename, "w", encoding='utf-8') as f:
    full_filename = folder + filename
    
    os.makedirs(os.path.dirname(full_filename), exist_ok=True)
    
    with open(full_filename, "w", encoding='utf-8') as f:
        f.write(content)

def download_web_page(page:ForumPage, visited_urls:set) -> list[ForumPage]:
        
    response = fetch_page(page.url)
    
    if response == None:
        return []
    
    save_html(response, page)
    
    return parse_page(response, page, visited_urls)

def main(first_page:str, visited_urls:set[str], test_cont:int=10):
    
    q = Queue()
    q.put(ForumPage(first_page))

    visited_urls.add(first_page)

    while not q.empty():
        page = q.get()
        
        links = download_web_page(page, visited_urls)
        if links:
            for x in links:
                q.put(x)

        test_cont -= 1
        
        if test_cont == 0:
            break
        
    return visited_urls