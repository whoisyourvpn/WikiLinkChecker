import requests
import re
import mwclient
from urllib.parse import unquote, urlparse

def login_to_wikipedia(username, password):
    site = mwclient.Site('en.wikipedia.org')
    site.login(username, password)
    return site

def update_reference_with_archive(ref, archive_url):
    archive_date_match = re.search(r'web\.archive\.org/web/(\d{4})(\d{2})(\d{2})', archive_url)
    if archive_date_match:
        archive_date = f'{archive_date_match.group(1)}-{archive_date_match.group(2)}-{archive_date_match.group(3)}'
    else:
        archive_date = 'Unknown'
    updated_ref = re.sub(r'}}$', f'|archive-url={archive_url}|archive-date={archive_date}|url-status=dead}}', ref)
    return updated_ref

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
            return 'Not Archived', 'N/A'
    except requests.RequestException:
        return 'Error Checking Archive', 'N/A'

def extract_page_name(input_text):
    if input_text.startswith('http'):
        url_parts = urlparse(input_text)
        page_name = unquote(url_parts.path.split('/')[-1])
    else:
        page_name = input_text
    return page_name

def main():
    username = input('Enter your Wikipedia username: ')
    password = input('Enter your Wikipedia password: ')
    site = login_to_wikipedia(username, password)

    input_text = input('Enter the Wikipedia page name or URL: ')
    page_name = extract_page_name(input_text)
    
    page = site.pages[page_name]
    page_content = page.text()

    cite_web_urls = re.findall(r'\{\{cite web[^}]*\|url=([^|}]+)', page_content, re.IGNORECASE)
    ref_urls = re.findall(r'<ref[^>]*>(?:[^<]*<a[^>]*href="([^"]+)"[^>]*>[^<]*</a>[^<]*)</ref>', page_content, re.IGNORECASE)
    all_urls = set(cite_web_urls + ref_urls)

    updated_content = page_content
    for url in all_urls:
        if 'archive.org' not in url:
            status = check_link_status(url)
            archive_status, archived_page = check_archive(url)
            if archive_status == 'Archived':
                updated_content = update_reference_with_archive(updated_content, archived_page)

    page.save(updated_content, summary='Updated dead links with archive URLs')

    print(f'Updated Wikipedia page: {page_name}')

if __name__ == '__main__':
    main()
