# -*- coding: utf-8 -*-
import concurrent.futures
import os
import re
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from urllib.parse import urlparse, quote

import requests
from bs4 import BeautifulSoup

DOMAIN = 'hentaivn.autos'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'
COMMON_HEADER = {
    "User-Agent": UA,
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}


@dataclass
class Tag:
    name: str
    desc: str

    def json(self):
        return {'name': self.name, 'desc': self.desc}


@dataclass
class Image:
    url: str

    def __hash__(self):
        return hash(self.url)

    def get_request(self) -> requests.Request:
        p = urlparse(self.url)

        headers = {
                      "Accept-Encoding": "gzip, deflate, br",
                      "Referer": f"{p.scheme}://{p.netloc}/",
                      "Sec-Fetch-Dest": "image",
                      "Sec-Fetch-Mode": "no-cors",
                      "Sec-Fetch-Site": "same-site",
                      "Sec-GPC": "1",
                      "Pragma": "no-cache",
                      "Cache-Control": "no-cache",
                      "TE": "trailers"
                  } | COMMON_HEADER

        return requests.Request("GET", self.url, headers=headers, params={"imgmax": "1200"})

    def file_name(self) -> str:
        return os.path.basename(urlparse(self.url).path)

    def json(self):
        return self.url


@dataclass
class Chapter:
    title: str
    url: str
    time: datetime
    domain: str

    def get_images(self) -> list[Image]:
        headers = {
                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                      'Referer': f'https://{self.domain}/{self.url}',
                      'Upgrade-Insecure-Requests': '1',
                      'Sec-Fetch-Dest': 'document',
                      'Sec-Fetch-Mode': 'navigate',
                      'Sec-Fetch-Site': 'same-origin',
                      'Sec-GPC': '1',
                  } | COMMON_HEADER

        response = requests.get(
            f'https://{self.domain}/{quote(self.url)}',
            headers=headers,
            params={'ie': 'utf-8'}
        )

        parser = BeautifulSoup(response.text, 'html.parser')
        pattern = re.compile(r'\?imgmax=[0-9]*$')
        return [Image(re.sub(pattern, '', img.attrs['data-src'])) for img in parser.select('img.lazyload')]

    def json(self):
        return {'title': self.title, 'url': self.url, 'time': self.time.strftime('%d/%m/%Y'), 'domain': self.domain}

    def download_all_images(self) -> dict[Image:BytesIO]:
        def download_image(image: Image) -> bytes:
            request = image.get_request()
            with requests.Session() as sss:
                pr = sss.prepare_request(request=request)
                return sss.send(request=pr).content

        images = self.get_images()
        finished = {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(download_image, image): image for image in images}
            for future in concurrent.futures.as_completed(future_to_url):
                image = future_to_url[future]
                content = future.result()
                finished[image] = content

        return finished


@dataclass
class Doc:
    title: str
    cover: Image
    tags: list[Tag]
    url: str
    domain: str

    def get_id(self) -> int:
        return int(self.url.removeprefix('/').split('-')[0])

    def get_name(self) -> str:
        pattern = re.compile(r'^/[0-9]*-doc-truyen-')
        return pattern.sub('', self.url)

    def get_chapters(self) -> list[Chapter]:
        headers = {
                      'Accept': '*/*',
                      'Referer': f'https://{self.domain}/list-showchapter.php?idchapshow={self.get_id()}&idlinkanime={self.get_name()}',
                      'Sec-Fetch-Dest': 'empty',
                      'Sec-Fetch-Mode': 'cors',
                      'Sec-Fetch-Site': 'same-origin',
                      'Sec-GPC': '1',
                  } | COMMON_HEADER

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
        return {'title': self.title, 'url': self.url, 'cover': self.cover.json(), 'domain': self.domain, 'tags': [x.json() for x in self.tags]}


def response2docs(response: requests.Response) -> list[Doc]:
    parser = BeautifulSoup(response.text, 'html.parser')

    _docs = []
    for doc in parser.select('li.item'):
        title = doc.select_one('div:nth-child(2) > p:nth-child(1) > a:nth-child(1)').text
        cover = doc.select_one('img').attrs['data-src']
        tags = [Tag(x.text, x.attrs['title']) for x in doc.select('span > a')]
        url = doc.select_one('div > a').attrs['href']
        # docs.append(Doc(title, Image(cover), tags, url, __DOMAIN))
        _docs.append(Doc(title, Image(cover), tags, url, DOMAIN))

    return _docs


def custom_url(url: str, pages: int = 1) -> dict[int, list[Doc]]:
    def single_custom(lurl: str, page: int) -> list[Doc]:
        lurl = f'{lurl}?page={page}'

        headers = {
                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                      'Referer': lurl,
                      'Upgrade-Insecure-Requests': '1',
                      'Sec-Fetch-Dest': 'document',
                      'Sec-Fetch-Mode': 'navigate',
                      'Sec-Fetch-Site': 'same-origin',
                      'Sec-Fetch-User': '?1',
                      'Sec-GPC': '1',
                  } | COMMON_HEADER

        params = {
            'page': page,
        }

        response = requests.get(lurl, params=params, headers=headers)
        pass
        return response2docs(response)

    docs = {}
    r = list(range(1, pages + 1))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(single_custom, url, page): page for page in r}
        for future in concurrent.futures.as_completed(future_to_url):
            page = future_to_url[future]
            docs[page] = future.result()

    return docs


def search(query: str, pages: int = 10) -> dict[int:list[Doc]]:
    def single_search(page: int) -> list[Doc]:
        headers = {
                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                      'Upgrade-Insecure-Requests': '1',
                      'Sec-Fetch-Dest': 'document',
                      'Sec-Fetch-Mode': 'navigate',
                      'Sec-Fetch-Site': 'cross-site',
                      'Sec-GPC': '1',
                      'Pragma': 'no-cache',
                      'Cache-Control': 'no-cache',
                  } | COMMON_HEADER

        params = {
            'key': query,
            'page': page,
        }

        response = requests.get(f'https://{DOMAIN}/tim-kiem-truyen.html', params=params, headers=headers)
        return response2docs(response)

    docs = {}
    r = list(range(1, pages + 1))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(single_search, page): page for page in r}
        for future in concurrent.futures.as_completed(future_to_url):
            page = future_to_url[future]
            docs[page] = future.result()

    return docs
