import requests
import re
from collections import Counter

def check_link_status(url):
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return 'Alive'
        else:
            return 'Dead'
    except requests.RequestException:
        return 'Dead'

def main():
    page_name = input('Enter the Wikipedia page name: ')
    api_url = f'https://en.wikipedia.org/w/rest.php/v1/page/{page_name}'
    response = requests.get(api_url)
    article_content = response.json().get('source', '')

    cite_web_templates = re.findall(r'\{\{cite web(.*?)\}\}', article_content, re.DOTALL)

    urls = []
    skipped_archived_links = 0
    for template in cite_web_templates:
        url_match = re.search(r'url=(https?://[^\s|]+)', template)
        archive_url_match = re.search(r'archive-url=(https?://[^\s|]+)', template)
        if url_match:
            url = url_match.group(1)
            if not archive_url_match:
                urls.append(url)
            else:
                skipped_archived_links += 1

    unique_urls = set(urls)
    total_links = len(unique_urls)
    processed_links = 0

    print(f'Total unique external links to process: {total_links}')
    print(f'Skipped archived links: {skipped_archived_links}')

    output_filename = f'{page_name}.txt'
    with open(output_filename, 'w') as output_file:
        for url in unique_urls:
            status = check_link_status(url)
            output_file.write(f'URL: {url}\n')
            output_file.write(f'|- Status: {status}\n|\n')
            processed_links += 1
            print(f'Processed {processed_links} of {total_links} links.')

    print(f'Results written to {output_filename}')

if __name__ == '__main__':
    main()
