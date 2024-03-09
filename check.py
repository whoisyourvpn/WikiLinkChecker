import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

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
            return 'Archived', data['archived_snapshots']['closest']['url']
        else:
            # Submit URL to the Wayback Machine if not archived
            save_url = f'https://web.archive.org/save/{url}'
            save_response = requests.get(save_url, timeout=10)
            if save_response.status_code == 200:
                return 'Submitted', save_url
            else:
                return 'Not Archived', 'N/A'
    except requests.RequestException:
        return 'Error Checking Archive', 'N/A'

def main():
    wikipedia_url = input('Enter the Wikipedia page URL: ')
    response = requests.get(wikipedia_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    page_name = urlparse(wikipedia_url).path.split('/')[-1]
    output_filename = f'{page_name}.txt'

    reflist_links = set()
    for div in soup.find_all('div', class_='reflist'):
        reflist_links.update(div.find_all('a', href=True))
    external_links = set(soup.find_all('a', class_='external text', href=True))
    all_links = reflist_links.union(external_links)
    filtered_links = [link for link in all_links if link['href'].startswith('http') and not any(domain in link['href'] for domain in ['archive.org', 'wikimedia.org', 'wikipedia.org', 'wikidata.org'])]

    unique_urls = set()
    for link in filtered_links:
        unique_urls.add(link['href'])

    total_links = len(unique_urls)
    processed_links = 0

    print(f'Total external links to process: {total_links}')

    with open(output_filename, 'w') as output_file:
        for url in unique_urls:
            status = check_link_status(url)
            archive_status, archived_page = check_archive(url)
            output_file.write(f'URL: {url}\n')
            output_file.write(f'|- Status: {status}\n')
            output_file.write(f'|- Archive: {archive_status}\n')
            output_file.write(f'|- Archived Page: {archived_page}\n|\n')
            processed_links += 1
            if processed_links % 5 == 0 or processed_links == total_links:
                print(f'Processed {processed_links} of {total_links} links. Continuing...')
                time.sleep(5)

    print(f'Results written to {output_filename}')

if __name__ == '__main__':
    main()
