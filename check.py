import requests
from bs4 import BeautifulSoup

def check_link_status(url):
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return 'Alive'
        else:
            return 'Dead'
    except requests.RequestException:
        return 'Dead'

def check_archive(url):
    archive_url = f'http://archive.org/wayback/available?url={url}'
    try:
        response = requests.get(archive_url, timeout=5)
        data = response.json()
        if data['archived_snapshots']:
            return 'Archived'
        else:
            return 'Not Archived'
    except requests.RequestException:
        return 'Error Checking Archive'

def main():
    wikipedia_url = input('Enter the Wikipedia page URL: ')
    response = requests.get(wikipedia_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    external_links = soup.find_all('a', href=True)
    for link in external_links:
        if link['href'].startswith('http'):
            status = check_link_status(link['href'])
            archive_status = check_archive(link['href'])
            print(f'URL: {link["href"]} | Status: {status} | Archive: {archive_status}')

if __name__ == '__main__':
    main()
