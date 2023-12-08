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


def timestamp(date: datetime) -> int:
    return int(date.timestamp())


@dataclass
class Link:
    text: str
    url: str

    def json(self):
        return {'url': self.url, 'text': self.text}


@dataclass
class Tag:
    name: str
    desc: str
    link: str

    def json(self):
        return {'name': self.name, 'desc': self.desc, 'link': self.link}


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
    time: int
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
        return {'title': self.title, 'url': self.url, 'time': self.time, 'domain': self.domain}

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
class DocInfo:
    name: str
    other_names: list[Link]
    characters: list[Link]
    cover: str
    tags: list[Tag]
    translators: list[Link]
    authors: list[Link]
    uploader: str
    status: Link
    description: str
    last_updated: int
    likes: int
    dislikes: int
    follow_at: Link

    def json(self):
        jj = {}
        if self.name is not None:
            jj['name'] = self.name
        if self.other_names is not None:
            jj['other_names'] = [x.json() for x in self.other_names]
        if self.characters is not None:
            jj['characters'] = [x.json() for x in self.characters]
        if self.cover is not None:
            jj['cover'] = self.cover
        if self.tags is not None:
            jj['tags'] = [x.json() for x in self.tags]
        if self.translators is not None:
            jj['translators'] = [x.json() for x in self.translators]
        if self.authors is not None:
            jj['authors'] = [x.json() for x in self.authors]
        if self.uploader is not None:
            jj['uploader'] = self.uploader
        if self.status is not None:
            jj['status'] = self.status.json()
        if self.description is not None:
            jj['description'] = self.description
        if self.last_updated is not None:
            jj['last_updated'] = self.last_updated
        if self.likes is not None:
            jj['likes'] = self.likes
        if self.dislikes is not None:
            jj['dislikes'] = self.dislikes
        if self.follow_at is not None:
            jj['follow_at'] = self.follow_at.json()

        return jj




def index_of_first_after(lst, predicate):
    for i, v in enumerate(lst):
        if predicate(v):
            return i + 1
    return None


# noinspection PyMethodMayBeStatic
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

            chapters.append(Chapter(title, link, timestamp(date), self.domain))

        return chapters

    # region janky ass parsing
    def handle_categories(self, parent, element):
        parent.tags = [Tag(x.text, x.attrs['title'], x.attrs['href']) for x in element.parent.findAll('a')]

    def handle_other_names(self, parent, element):
        parent.other_names = [Link(x.text, x.attrs['href']) for x in element.parent.findAll('a')]

    def handle_translator(self, parent, element):
        parent.translators = [Link(x.text, x.attrs['href']) for x in element.parent.findAll('a')]

    def handle_author(self, parent, element):
        parent.authors = [Link(x.text, x.attrs['href']) for x in element.parent.findAll('a')]

    def handle_status(self, parent, element):
        parent.status = [Link(x.text, x.attrs['href']) for x in element.parent.findAll('a')][0]

    def handle_characters(self, parent, element):
        parent.characters = [Link(x.text, x.attrs['href']) for x in element.parent.findAll('a')]

    def handle_description(self, parent, element):
        lst = list(element.parent.parent.findAll('p'))
        parent.description = lst[index_of_first_after(lst, lambda x: x.text.startswith("Nội dung"))].text

    def handle_follow_at(self, parent, element):
        parent.follow_at = [Link(x.text, x.attrs['href']) for x in element.parent.findAll('a')][0]

    def handle_uploader(self, parent, element):
        parent.uploader = element.parent.text.removeprefix('Thực hiện: ')

    def get_metadata(self):
        headers = {
                      'Referer': f'https://{self.domain}/${self.url}'.encode(),
                      'Sec-Fetch-Dest': 'document',
                      'Sec-Fetch-Mode': 'navigate',
                      'Sec-Fetch-Site': 'same-origin',
                      'Sec-GPC': '1',
                  } | COMMON_HEADER

        response = requests.get(f'https://{self.domain}/{self.url}'.encode(), headers=headers)

        handlers = {
            "Thể Loại:": self.handle_categories,
            "Nhóm dịch:": self.handle_translator,
            "Tên Khác: ": self.handle_other_names,
            "Tác giả: ": self.handle_author,
            "Tình Trạng: ": self.handle_status,
            "Nội dung:": self.handle_description,
            "Theo dõi tại:": self.handle_follow_at,
            "Nhân vật: ": self.handle_characters,
            "Thực hiện:": self.handle_uploader,
        }

        soup = BeautifulSoup(response.text, 'html.parser')
        page_info = soup.find('div', {'class': 'page-info'})
        doc = DocInfo(None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        doc.name = page_info.find('a').text.removeprefix("\n").removesuffix("\n")
        doc.last_updated = timestamp(datetime.strptime(page_info.find('i').text, '%H:%M - %d/%m/%Y'))
        doc.likes = int(soup.find('div', {'class': 'but_like'}).text)
        doc.dislikes = int(soup.find('div', {'class': 'but_unlike'}).text)
        doc.cover = soup.select_one('.page-ava > img').attrs['src']

        for pElement in page_info.findAll('p'):
            span = pElement.find('span')
            if span is None or pElement is None:
                continue

            if span.text in handlers.keys():
                handlers[span.text](doc, span)

        return doc

    # endregion

    def json(self):
        return {'title': self.title, 'url': self.url, 'cover': self.cover.json(), 'domain': self.domain,
                'tags': [x.json() for x in self.tags]}


def response2docs(response: requests.Response) -> list[Doc]:
    parser = BeautifulSoup(response.text, 'html.parser')

    _docs = []
    for doc in parser.select('li.item'):
        title = doc.select_one('div:nth-child(2) > p:nth-child(1) > a:nth-child(1)').text
        cover = doc.select_one('img').attrs['data-src']
        tags = [Tag(x.text, x.attrs['title'], x.attrs['href']) for x in doc.select('span > a')]
        url = doc.select_one('div > a').attrs['href']
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
