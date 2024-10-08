import json
import requests
import logging

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'


class Domain:
    domain: str = None

    # multiple urls, one link per url
    @staticmethod
    def get_remote_sources():
        with open('config.json', 'r') as f:
            sources = json.loads(f.read())['remote-sources']
        return sources

    @staticmethod
    def test_remote_source(s: str):
        try:
            logging.info(f'about to resolve {s}')
            test_domain = requests.get(s).text.strip()
            test_request = requests.get(f'https://{test_domain}', headers={'User-Agent': UA})
            target_domain = test_request.url.removeprefix('https://').removesuffix('/')
            logging.info(f'{s} -> {test_domain} -> {target_domain}')
            if '<a href="/forum/search-plus.php">Tìm kiếm nâng cao</a>' in test_request.text:
                # skip multiple redirects and image referrer errors
                return target_domain
        except Exception as e:
            pass

    @staticmethod
    def get_first_domain():
        for sr in Domain.get_remote_sources():
            r = Domain.test_remote_source(sr)
            if r is not None:
                return r

    @staticmethod
    def update_domain():
        Domain.domain = Domain.get_first_domain()
        return Domain.domain

    @staticmethod
    def get_domain():
        if Domain.domain is None:
            Domain.update_domain()
        return Domain.domain
