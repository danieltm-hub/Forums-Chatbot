import requests
from bs4 import BeautifulSoup

def fetch_page(url):
    """Realiza una solicitud GET a la URL y devuelve el contenido de la página."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions as e:
        print(f"Error al acceder a {url}: {e}")
        return None
    
def parse_page(html):
    """Analiza el contenido HTML y extrae los links."""

    soup = BeautifulSoup(html, "html.parser")

    links = []
    for link in soup.find_all('a', href=True):
        links.append(link['href'])

    return links

