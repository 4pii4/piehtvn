# -*- coding: utf-8 -*-
import concurrent.futures
import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse, quote

import requests
from bs4 import BeautifulSoup

DOMAIN = 'hentaivn.autos'


@dataclass
class Tag:
    name: str
    desc: str

    def json(self):
        return {'name': self.name, 'desc': self.desc}


@dataclass
class Image:
    url: str

    def get_request(self) -> requests.Request:
        querystring = {"imgmax": "1200"}
        p = urlparse(self.url)
        payload = ""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
            "Accept": "image/avif,image/webp,*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": f"{p.scheme}://{p.netloc}/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "Sec-GPC": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "trailers"
        }

        return requests.Request("GET", self.url, data=payload, headers=headers, params=querystring)

    def json(self):
        return self.url


@dataclass
class Chapter:
    title: str
    url: str
    date: datetime
    domain: str

    def get_images(self) -> list[Image]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': f'https://{self.domain}/{self.url}',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
        }

        response = requests.get(
            f'https://{self.domain}/{quote(self.url)}',
            headers=headers,
            params={'ie': 'utf-8'}
        )

        parser = BeautifulSoup(response.text, 'html.parser')
        pattern = re.compile(r'\?imgmax=[0-9]*$')
        return [Image(re.sub(pattern, '', img.attrs['data-src'])) for img in parser.select('img.lazyload')]

    def json(self):
        return {'title': self.title, 'url': self.url, 'date': self.date}


@dataclass
class Doc:
    title: str
    cover: Image
    # tags: list[Tag]
    url: str
    domain: str

    def get_id(self) -> int:
        return int(self.url.removeprefix('/').split('-')[0])

    def get_name(self) -> str:
        pattern = re.compile(r'^/[0-9]*-doc-truyen-')
        return pattern.sub('', self.url)

    def get_chapters(self) -> list[Chapter]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': f'https://{self.domain}/list-showchapter.php?idchapshow={self.get_id()}&idlinkanime={self.get_name()}',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
        }

        params = {
            'idchapshow': self.get_id(),
            'idlinkanime': self.get_name(),
        }

        response = requests.get(f'https://{self.domain}/list-showchapter.php', params=params, headers=headers)
        parser = BeautifulSoup(response.text, 'html.parser')

        tds = parser.select('tr > td')
        mains = tds[0::2]
        metas = tds[1::2]

        chapters = []
        for main, meta in zip(mains, metas):
            date = datetime.strptime(meta.text, '%d/%m/%Y')
            title = main.select_one('td > a > h2').text
            link = main.select_one('td > a').attrs['href']

            chapters.append(Chapter(title, link, date, self.domain))

        return chapters

    def json(self):
        # return {'title': self.title, 'cover': self.cover.json(), 'tags': [tag.json() for tag in self.tags], 'url': self.url, 'domain': self.domain}
        return {'title': self.title, 'url': self.url, 'cover': self.cover.json(), 'domain': self.domain}


def search(query: str, pages: int = 10) -> dict[int:Doc]:
    def single_search(page: int) -> list[Doc]:
        print(f'single search {query} {page}')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-GPC': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        params = {
            'key': query,
            'page': page,
        }

        response = requests.get(f'https://{DOMAIN}/tim-kiem-truyen.html', params=params, headers=headers)
        parser = BeautifulSoup(response.text, 'html.parser')

        _docs = []
        for doc in parser.select('li.item'):
            title = doc.select_one('div:nth-child(2) > p:nth-child(1) > a:nth-child(1)').text
            cover = doc.select_one('img').attrs['data-src']
            # tags = [Tag(x.text, x.attrs['title']) for x in doc.select('span > a')]
            url = doc.select_one('div > a').attrs['href']
            # docs.append(Doc(title, Image(cover), tags, url, __DOMAIN))
            _docs.append(Doc(title, Image(cover), url, DOMAIN))

        return _docs

    docs = {}
    r = list(range(1, pages + 1))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(single_search, page): page for page in r}
        for future in concurrent.futures.as_completed(future_to_url):
            page = future_to_url[future]
            docs[page] = future.result()

    return docs
