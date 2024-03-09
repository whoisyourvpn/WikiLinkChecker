import requests
import re
from urllib.parse import quote, urlparse

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
        page_name = url_parts.path.split('/')[-1]
    else:
        page_name = input_text
    return page_name

def main():
    input_text = input('Enter the Wikipedia page name or URL: ')
    page_name = extract_page_name(input_text)
    formatted_page_name = quote(page_name.replace(' ', '_'))
    
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": formatted_page_name,
        "rvprop": "content",
        "format": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Access the source in the revisions section
    pages = data['query']['pages']
    for page_id in pages:
        page = pages[page_id]
        if 'revisions' in page:
            page_content = page['revisions'][0]['*']

    # Find URLs within {{cite web}} and <ref> tags
    cite_web_urls = re.findall(r'\{\{cite web[^}]*\|url=([^|}]+)', page_content, re.IGNORECASE)
    ref_urls = re.findall(r'<ref[^>]*>(?:[^<]*<a[^>]*href="([^"]+)"[^>]*>[^<]*</a>[^<]*)</ref>', page_content, re.IGNORECASE)
    all_urls = set(cite_web_urls + ref_urls)  # Combine and remove duplicates

    # Count skipped archived links
    skipped_archived_links = sum(1 for url in all_urls if 'archive.org' in url)

    output_filename = f'{page_name}_results.txt'
    with open(output_filename, 'w') as output_file:
        for url in all_urls:
            if 'archive.org' not in url:
                status = check_link_status(url)
                archive_status, archived_page = check_archive(url)
                output_file.write(f'URL: {url}\n')
                output_file.write(f'|- Status: {status}\n')
                output_file.write(f'|- Archive: {archive_status}\n')
                if archive_status == 'Archived':
                    output_file.write(f'|- Archived Page: {archived_page}\n')
                else:
                    output_file.write(f'|- Archived Page: N/A\n')
                output_file.write('|\n')

    print(f'Results written to {output_filename}')
    print(f'Skipped archived links: {skipped_archived_links}')

if __name__ == '__main__':
    main()
