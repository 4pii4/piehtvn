# -*- coding: utf-8 -*-
import collections.abc
import concurrent.futures
import datetime
import io
import logging
import os
import re
import time
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from domain import Domain

import requests
import six
from bs4 import BeautifulSoup

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'
COMMON_HEADER = {
    "User-Agent": UA,
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

last_reload = -1


def reload():
    global last_reload
    if time.time() - last_reload > 30:
        last_reload = time.time()
        # do all the reloading here
        return f'<title>Domain updated!</title><p>Successfully updated domain to {Domain.update_domain()}</p>'
    else:
        return f'<title>Domain not updated!</title><p>Rate-limited due to too many requests. ' + \
               f'Please wait {int(30 - (time.time() - last_reload))} seconds.</p> '


def timestamp(date: datetime) -> int:
    return int(date.timestamp())


def index_of_first_after(lst, predicate):
    for i, v in enumerate(lst):
        if predicate(v):
            return i + 1
    return None


def iterable(arg):
    return (
            isinstance(arg, collections.abc.Iterable)
            and not isinstance(arg, six.string_types)
    )


def parallel_map(lst, func) -> dict:
    d = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        f = {executor.submit(func, i): i for i in lst}
        for future in concurrent.futures.as_completed(f):
            k = f[future]
            d[k] = future.result()
    return d


def linkify(txt):
    return txt.removeprefix('/').removesuffix('.html')


class Base:
    @staticmethod
    def subjson(x):
        if hasattr(x, 'json'):
            return x.json()
        else:
            return x

    def json(self):
        d = {}
        for key, val in self.__dict__.items():
            if val is None:
                continue

            if iterable(val):
                d[key] = [self.subjson(i) for i in val]
            else:
                d[key] = self.subjson(val)
        return d


@dataclass
class Link(Base):
    text: str
    url: str


@dataclass
class Tag(Base):
    name: str
    desc: str
    link: str


@dataclass
class Image(Base):
    url: str

    def __hash__(self):
        return hash(self.url)

    def get_request(self) -> requests.Request:
        # logging.info(f'trying to download {self.url}')
        # p = urllib.parse.urlparse(self.url)
        # ref = f"https://{p.netloc}"
        # if p.netloc.startswith("up"):
        ref = f"https://{Domain.get_domain()}"

        headers = {
                      "Accept-Encoding": "gzip, deflate, br",
                      "Referer": ref,
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
        return os.path.basename(urllib.parse.urlparse(self.url).path)


@dataclass
class Chapter(Base):
    title: str
    url: str
    time: int
    domain: str

    def get_id(self) -> int:
        return int(self.url.split('-')[1])

    def get_images(self) -> dict:
        def default_cdn() -> list[str]:
            accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            headers = {
                          'Accept': accept,
                          'Referer': f'https://{Domain.get_domain()}/{self.url}'.encode(),
                          'Upgrade-Insecure-Requests': '1',
                          'Sec-Fetch-Dest': 'document',
                          'Sec-Fetch-Mode': 'navigate',
                          'Sec-Fetch-Site': 'same-origin',
                          'Sec-GPC': '1',
                      } | COMMON_HEADER

            response = requests.get(
                f'https://{Domain.get_domain()}/{urllib.parse.quote(self.url)}'.encode(),
                headers=headers,
                params={'ie': 'utf-8'}
            )

            parser = BeautifulSoup(response.text, 'html.parser')
            pattern = re.compile(r'\?imgmax=\d*$')
            return [re.sub(pattern, '', img.attrs['data-src']) for img in parser.select('img.lazyload')]

        def custom_cdn(n: int) -> list[str]:
            headers = {
                          'Accept': '*/*',
                          'Referer': f'https://{Domain.get_domain()}/ajax_load_server.php',
                          'Content-Type': 'application/x-www-form-urlencoded',
                          'X-Requested-With': 'XMLHttpRequest',
                          'Origin': f'https://{Domain.get_domain()}',
                          'Sec-Fetch-Dest': 'empty',
                          'Sec-Fetch-Mode': 'cors',
                          'Sec-Fetch-Site': 'same-origin',
                      } | COMMON_HEADER

            data = {
                'server_id': self.get_id(),
                'server_type': str(n),
            }

            response = requests.post(f'https://{Domain.get_domain()}/ajax_load_server.php', headers=headers, data=data)
            soup = BeautifulSoup(response.text, 'html.parser')
            pattern = re.compile(r'\?imgmax=\d*$')
            return [re.sub(pattern, '', img['src']) for img in soup.select('img')]

        def work(worktype: str) -> list[str]:
            if worktype == 'default':
                return default_cdn()
            elif re.match('cdn[12]', worktype):
                return custom_cdn(int(worktype.removeprefix('cdn')))
            else:
                return []

        return parallel_map(['default', 'cdn1', 'cdn2'], work)

    def download_all_images(self) -> dict[Image:io.BytesIO]:
        def download_image(image: Image) -> bytes:
            request = image.get_request()
            with requests.Session() as sss:
                pr = sss.prepare_request(request=request)
                return sss.send(request=pr).content

        images = [Image(x) for x in self.get_images()]
        finished = parallel_map(images, download_image)

        return finished


@dataclass
class DocInfo(Base):
    cover: str
    id: int
    name: str
    other_names: list[str]
    tags: list[Tag]
    translators: list[Link]
    authors: list[str]
    characters: list[str]
    doujinshi: str
    uploader: str
    status: str
    desc: str
    last_updated: int
    likes: int
    dislikes: int
    follow_at: Link


@dataclass
class Doc(Base):
    name: str
    url: str
    cover: str
    tags: list[Tag]
    domain: str

    def get_id(self) -> int:
        return int(self.url.removeprefix('/').split('-')[0])

    def get_name(self) -> str:
        pattern = re.compile(r'^\d*-doc-truyen-')
        return pattern.sub('', self.url)

    def get_chapters(self) -> list[Chapter]:
        ref = (f'https://{Domain.get_domain()}/list-showchapter.php' +
               f'?idchapshow={self.get_id()}&idlinkanime={self.get_name()}').encode()
        headers = {
                      'Accept': '*/*',
                      'Referer': ref,
                      'Sec-Fetch-Dest': 'empty',
                      'Sec-Fetch-Mode': 'cors',
                      'Sec-Fetch-Site': 'same-origin',
                      'Sec-GPC': '1',
                  } | COMMON_HEADER

        params = {
            'idchapshow': self.get_id(),
            'idlinkanime': self.get_name(),
        }

        response = requests.get(f'https://{Domain.get_domain()}/list-showchapter.php'.encode(), params=params,
                                headers=headers)
        parser = BeautifulSoup(response.text, 'html.parser')

        tds = parser.select('tr > td')
        mains = tds[0::2]
        metas = tds[1::2]

        chapters = []
        for main, meta in zip(mains, metas):
            date = datetime.strptime(meta.text, '%d/%m/%Y')
            title = main.select_one('td > a > h2').text
            link = linkify(main.select_one('td > a').attrs['href'])

            chapters.append(Chapter(title, link, timestamp(date), Domain.get_domain()))

        return chapters

    def get_metadata(self):
        def handle_categories(parent, element):
            parent.tags = [Tag(x.text, x.attrs['title'], linkify(x.attrs['href'])) for x in element.parent.findAll('a')]

        def handle_other_names(parent, element):
            parent.other_names = [x.text for x in element.parent.findAll('a')]

        def handle_translator(parent, element):
            parent.translators = [Link(x.text, linkify(x.attrs['href'])) for x in element.parent.findAll('a')]

        def handle_author(parent, element):
            parent.authors = [x.text for x in element.parent.findAll('a')]

        def handle_status(parent, element):
            parent.status = element.parent.find('a').text

        def handle_characters(parent, element):
            parent.characters = [x.text for x in element.parent.findAll('a')]

        def handle_description(parent, element):
            lst = list(element.parent.parent.findAll('p'))
            parent.desc = lst[index_of_first_after(lst, lambda x: x.text.startswith("Nội dung"))].text

        def handle_follow_at(parent, element):
            e = element.parent.find('a')
            parent.follow_at = Link(e.text, linkify(e.attrs['href']))

        def handle_uploader(parent, element):
            parent.uploader = element.parent.text.removeprefix('Thực hiện: ')

        def handle_doujinshi(parent, element):
            parent.doujinshi = element.parent.find('a').text

        headers = {
                      'Referer': f'https://{Domain.get_domain()}/${self.url}'.encode(),
                      'Sec-Fetch-Dest': 'document',
                      'Sec-Fetch-Mode': 'navigate',
                      'Sec-Fetch-Site': 'same-origin',
                      'Sec-GPC': '1',
                  } | COMMON_HEADER

        response = requests.get(f'https://{Domain.get_domain()}/{self.url}'.encode(), headers=headers)

        handlers = {
            "Tên Khác": handle_other_names,
            "Thể Loại": handle_categories,
            "Nhóm dịch": handle_translator,
            "Tác giả": handle_author,
            "Nhân vật": handle_characters,
            "Doujinshi": handle_doujinshi,
            "Thực hiện": handle_uploader,
            "Tình Trạng": handle_status,
            "Nội dung": handle_description,
            "Theo dõi tại": handle_follow_at,
        }

        soup = BeautifulSoup(response.text, 'html.parser')
        page_info = soup.find('div', {'class': 'page-info'})
        # noinspection PyTypeChecker
        doc = DocInfo(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        doc.cover = soup.select_one('.page-ava > img').attrs['src']
        doc.id = int(soup.select_one('#myInputxx').attrs['value'])
        doc.name = page_info.find('a').text.removeprefix("\n").removesuffix("\n")
        doc.likes = int(soup.find('div', {'class': 'but_like'}).text)
        doc.dislikes = int(soup.find('div', {'class': 'but_unlike'}).text)
        doc.last_updated = timestamp(datetime.strptime(page_info.find('i').text, '%H:%M - %d/%m/%Y'))

        for pElement in page_info.findAll('p'):
            span = pElement.find('span')
            if span is None or pElement is None:
                continue

            for handler in handlers.keys():
                if span.text.startswith(handler):
                    handlers[handler](doc, span)

        return {'details': doc, 'from': linkify(response.url) + '.html'}


@dataclass
class TagPage(Base):
    tag_name: str
    tag_desc: str
    url: str
    domain: str
    docs: list[Doc]


def response2docs(response: requests.Response) -> (list[Doc], int):
    parser = BeautifulSoup(response.text, 'html.parser')

    _docs = []
    for doc in parser.select('li.item'):
        title = doc.select_one('div:nth-child(2) > p:nth-child(1) > a:nth-child(1)').text
        cover = doc.select_one('img').attrs['data-src']
        tags = [Tag(x.text, x.attrs['title'], linkify(x.attrs['href'])) for x in doc.select('span > a')]
        url = linkify(doc.select_one('div > a').attrs['href'])
        _docs.append(Doc(title, url, cover, tags, Domain.get_domain()))

    maxpage = 1
    pagebuttons = [x for x in parser.select('.pagination > li')]
    pagenumbers = []
    if len(pagebuttons) > 0:
        for pb in pagebuttons:
            ia = pb.select_one('a')
            ib = pb.select_one('b')
            if ia is not None and ia.text.isnumeric():
                pagenumbers.append(int(ia.text))
            if ib is not None and ib.text.isnumeric():
                pagenumbers.append(int(ib.text))
        maxpage = max(pagenumbers)

    return _docs, maxpage


def custom_url(url: str, page: int = 1) -> (list[Doc], int):
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
        'page': page,
    }

    print(url, page)

    response = requests.get(f'https://{Domain.get_domain()}/{url}', params=params, headers=headers)
    docs, maxpage = response2docs(response)
    if page > maxpage:
        docs.clear()
    return {'docs': docs, 'maxpage': maxpage}


def search(query: str, page: int = 1) -> (list[Doc], int):
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
        'key': query.encode(),
        'page': page,
    }

    response = requests.get(f'https://{Domain.get_domain()}/tim-kiem-truyen.html', params=params, headers=headers)
    docs, maxpage = response2docs(response)
    if page > maxpage:
        docs.clear()
    return {'docs': docs, 'maxpage': maxpage}


def homepage() -> dict[str:list[Doc]]:
    def get_trending() -> list[Doc]:
        accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/jxl,image/webp,*/*;q=0.8'
        headers = {
                      'Accept': accept,
                      'Upgrade-Insecure-Requests': '1',
                      'Sec-Fetch-Dest': 'document',
                      'Sec-Fetch-Mode': 'navigate',
                      'Sec-Fetch-Site': 'cross-site',
                      'Sec-GPC': '1',
                      'Pragma': 'no-cache',
                      'Cache-Control': 'no-cache',
                  } | COMMON_HEADER

        response = requests.get(f'https://{Domain.get_domain()}/', headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        trending = []
        for t in soup.select('#myDIV > ul > li'):
            namelink = t.select_one('.box-description')
            cover = re.sub(r'.*:url\(([^)]*)\);.*', r'\1', t.select_one('li > div > a > div')['style'])
            name = namelink.select_one('h2').text
            link = linkify(namelink.select_one('a')['href'])
            trending.append(Doc(name, link, cover, [], Domain.get_domain()))
        return trending

    def get_recent() -> list[Doc]:
        cookies = {
            'tataxoff': '1',
        }

        headers = {
                      'Accept': '*/*',
                      'Referer': f'https://{Domain.get_domain()}/list-moicapnhat-doc.php',
                      'Sec-Fetch-Dest': 'empty',
                      'Sec-Fetch-Mode': 'cors',
                      'Sec-Fetch-Site': 'same-origin',
                      'Sec-GPC': '1',
                      'Pragma': 'no-cache',
                      'Cache-Control': 'no-cache',
                  } | COMMON_HEADER

        response = requests.get(f'https://{Domain.get_domain()}/list-moicapnhat-doc.php', cookies=cookies,
                                headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        recent = []
        for t in soup.select('.item > ul'):
            link = linkify(t.select_one('a')['href'])
            name = t.select_one('span > a > h2').text
            cover = t.select_one('img')['src']
            recent.append(Doc(name, link, cover, [], Domain.get_domain()))
        return recent

    def work(worktype: str) -> list[Doc]:
        if worktype == 'trending':
            return get_trending()
        elif worktype == 'recent':
            return get_recent()

    tasks = ['trending', 'recent']
    results = parallel_map(tasks, work)

    return results
