import requests
from bs4 import BeautifulSoup
import os

def check_link_status(url):
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return 'Alive'
        else:
            return 'Dead'
    except requests.RequestException:
        return 'Dead'

def check_and_submit_archive(url):
    archive_url = f'http://archive.org/wayback/available?url={url}'
    try:
        response = requests.get(archive_url, timeout=5)
        data = response.json()
        if data['archived_snapshots']:
            return data['archived_snapshots']['closest']['url'], 'Archived'
        else:
            # Submit URL to the Wayback Machine for archiving
            save_url = f'https://web.archive.org/save/{url}'
            save_response = requests.get(save_url, timeout=5)
            if save_response.status_code == 200:
                return save_url, 'Submitted for Archiving'
            else:
                return 'N/A', 'Error Submitting for Archiving'
    except requests.RequestException:
        return 'N/A', 'Error Checking Archive'

def main():
    wikipedia_url = input('Enter the Wikipedia page URL: ')
    response = requests.get(wikipedia_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    page_name = wikipedia_url.split('/')[-1] + '.txt'
    with open(page_name, 'w', encoding='utf-8') as file:
        external_links = soup.find_all('a', href=True)
        for link in external_links:
            if link['href'].startswith('http'):
                status = check_link_status(link['href'])
                archive_link, archive_status = check_and_submit_archive(link['href'])
                file.write(f'URL: {link["href"]} | Status: {status} | Archive: {archive_status} | Archived Page: {archive_link}\n')

if __name__ == '__main__':
    main()
