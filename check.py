import requests
import re

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
    page_content = response.json()['source']

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
                output_file.write(f'URL: {url}\n|- Status: {status}\n|\n')

    print(f'Results written to {output_filename}')
    print(f'Skipped archived links: {skipped_archived_links}')

if __name__ == '__main__':
    main()
