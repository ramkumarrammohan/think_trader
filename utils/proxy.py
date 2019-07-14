import requests
from bs4 import BeautifulSoup


def get_proxies_bsoup():
    res = requests.get('https://free-proxy-list.net/',
                       headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(res.text, "lxml")
    proxy_containter = []
    for items in soup.select("tbody tr"):
        proxy_list = ':'.join([item.text for item in items.select("td")[:2]])
        proxy_containter.append(proxy_list)
        # print(proxy_list)
    print("{} proxy found".format(len(proxy_containter)))
    return proxy_containter
