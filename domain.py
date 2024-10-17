
import requests
import logging

import piehtvn_config

requests.packages.urllib3.util.connection.HAS_IPV6 = piehtvn_config.use_ipv6


class Domain:
    domain: str = None

    @staticmethod
    def test_remote_source(s: str):
        result = None

        try:
            logging.info(f'about to resolve {s}')
            test_domain = requests.get(s).text.strip()
            test_request = requests.get(f'https://{test_domain}', headers={'User-Agent': piehtvn_config.user_agent})
            # skip multiple redirects and image referrer errors
            target_domain = test_request.url.removeprefix('https://').removesuffix('/')
            logging.info(f'{s} -> {test_domain} -> {target_domain}')
            if '<a href="/forum/search-plus.php">Tìm kiếm nâng cao</a>' in test_request.text:
                result = target_domain
        except Exception as e:
            pass
        return result

    @staticmethod
    def get_first_domain():
        for sr in piehtvn_config.remote_sources:
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
