This Python tool checks the status of external links on a specified Wikipedia page, determines if they are alive or dead, and cross-references them with the Wayback Machine to check for archived versions. If a link is not already archived, the tool attempts to submit it to the Wayback Machine. The results are output to a text file named after the Wikipedia page, providing a clear and readable report of the link statuses and archive information.

**Features:**

-   Checks the status of external links on a Wikipedia page.
-   Cross-references links with the Wayback Machine for archival status.
-   Submits unarchived links to the Wayback Machine.
-   Ignores links from `*.wikipedia.org` and `*.wikidata.org`.
-   Outputs results to a text file with a readable format.

**Requirements:**

-   Python 3
-   `requests` library
-   `beautifulsoup4` library

**Usage:**

1.  Install the required libraries: `pip install beautifulsoup4 requests`.
2.  Run the script and enter the URL of the Wikipedia page when prompted.
3.  Check the output text file for the link status report.
