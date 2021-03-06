import re
import requests
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd

original_url = input("Enter the website url: ")

un_scraped = deque([original_url])

scraped = set()

emails = set()

while len(un_scraped):
    url = un_scraped.popleft()
    scraped.add(url)

    parts = urlsplit(url)
    # SplitResult(scheme='https', netloc='www.google.com', path='/example', query='', fragment='')
    base_url = "{0.scheme}://{0.netloc}".format(parts)
    if '/' in parts.path:
        path = url[:url.rfind('/') + 1]
    else:
        path = url

    print("Crawling URL %s" % url)
    try:
        response = requests.get(url)
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
        continue

    new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))
    emails.update(new_emails)

    soup = BeautifulSoup(response.text, 'lxml')

    for anchor in soup.find_all("a"):
        if "href" in anchor.attrs:
            link = anchor.attrs["href"]
        else:
            link = ''

            if link.startswith('/'):
                link = base_url + link

            elif not link.startswith('http'):
                link = path + link

            if not link.endswith(".gz"):
                if link not in un_scraped and link not in scraped:
                    un_scraped.append(link)

df = pd.DataFrame(emails, columns=["Email"])

print(df)
df.to_csv('email.csv', index=False)
