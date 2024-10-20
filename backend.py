import dataclasses
import json
import platform
import re
import subprocess
from datetime import timedelta
from functools import wraps
import logging

from bottle import Bottle, request, response, template

from piehtvn import *
import piehtvn_config


def main():
    start_time = time.time()

    whoami_output = subprocess.check_output(['whoami']).decode('utf-8').strip()
    commitid = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    commitid_short = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
    if platform.system() == 'Windows':
        platformwin = platform.win32_ver()
        osver = f'Windows {platformwin[0]} build {platformwin[1]}'
    else:
        osver = subprocess.check_output(['uname', '-sr']).decode('utf-8').strip()

    app = Bottle()

    def log_to_logger(fn):
        @wraps(fn)
        def _log_to_logger(*args, **kwargs):
            actual_response = fn(*args, **kwargs)
            logging.info('%s %s %s %s' % (request.remote_addr, request.method, request.url, response.status))
            return actual_response

        return _log_to_logger

    def generate_response(obj):
        class EnhancedJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if dataclasses.is_dataclass(o):
                    return dataclasses.asdict(o)
                return super().default(o)

        response.set_header('Access-Control-Allow-Origin', '*')
        response.content_type = 'application/json'
        return json.dumps(obj, ensure_ascii=False, cls=EnhancedJSONEncoder)

    def uptime_calculate():
        return str(timedelta(seconds=round(time.time()) - round(start_time)))

    @app.route('/')
    def root():
        def li(s: str) -> str:
            return f'<li><a href="{s}" target="blank"><code>{s}</code></a></li>'

        examples = [
            '/search?query=liyue',
            '/homepage',
            '/get-chapters?url=36048-doc-truyen-genshin-liyue-du-ky',
            '/get-metadata?url=36048-doc-truyen-genshin-liyue-du-ky',
            '/get-images?url=36048-67609-xem-truyen-genshin-liyue-du-ky-ganyu',
            '/download-image?url=https://i3.hhentai.net/images/2024/01/27/1706374832-16.jpg',
            '/tag/the-loai-133-big_ass.html',
            '/reload'
        ]

        return template('''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>PieHTVN</title>
    <style type="text/css">
      html { background-color: #eee; font-family: sans; }
      body { background-color: #fff; border: 1px solid #ddd; padding: 15px; margin: 15px; }
      pre, code { background-color: #818b981f; color: black; border-radius: 5px; padding: 3px; font-family: "Courier New", Courier, monospace; }
    </style>
  </head>
  <body>
    <h1>Welcome to <a href="https://github.com/4pii4/piehtvn">PieHTVN</a></h1>
    <p>Backend is running as <code>{{user}}</code> on <code>{{osver}}</code></p>
    <p>
      Current git commit: <code><a href="https://github.com/4pii4/piehtvn/commit/{{commitid}}">{{commitid_short}}</a></code>
    </p>
    <p>Current HentaiVN domain: <a href="https://{{domain}}">{{domain}}</a></p>
    <p>Uptime: <code>{{uptime}}</code></p>
    <p>Quick start:
    <ul>
''' + '\n'.join([li(s) for s in examples]) +
                        '''
    </ul></p>
  </body>
</html>

''', user=whoami_output, osver=osver, commitid=commitid, commitid_short=commitid_short, domain=Domain.get_domain(),
                        uptime=uptime_calculate())

    @app.route('/homepage')
    def backend_homepage():
        return generate_response(homepage())

    @app.route('/search')
    def backend_search():
        if request.query.query is None:
            return 'missing query parameter'
        query = request.query.query
        page = int(request.query.page or 1)

        return generate_response(search(query, page))

    # noinspection PyTypeChecker
    @app.route('/get-chapters')
    def backend_get_chapters():
        doc = Doc(None, request.query.url, None, None, Domain.get_domain())
        return generate_response(doc.get_chapters())

    # noinspection PyTypeChecker
    @app.route('/get-metadata')
    def backend_get_chapter_metadata():
        doc = Doc(None, request.query.url.removeprefix('.html') + '.html', None, None, Domain.get_domain())
        return generate_response(doc.get_metadata())

    # noinspection PyTypeChecker
    @app.route('/get-images')
    def backend_get_images():
        chapter = Chapter(None, request.query.url.removeprefix('.html') + '.html', None, Domain.get_domain())
        return generate_response(chapter.get_images())

    @app.route('/download-image')
    def backend_download_image():
        img = Image(request.query.url)
        response.set_header('Access-Control-Allow-Origin', '*')
        response.content_type = f'image/{img.url.split(".")[-1]}'
        with requests.Session() as session:
            resp = session.send(img.get_request().prepare())
        return resp.content

    @app.route('/tag/<tag>')
    def backend_tag(tag: str):
        page = int(request.query.page or 1)
        if re.match('^the-loai-[0-9]+-[a-z_0-9]*(\\.html)?$', tag): # have the number thingy
            return generate_response(custom_url(tag, page))
        elif re.match('^the-loai-[a-z_0-9]+(\\.html)?$', tag):
            from piehtvn import COMMON_HEADER
            resp = requests.post(f'https://{Domain.get_domain()}/tag_box.php', headers=COMMON_HEADER)
            soup = BeautifulSoup(resp.text, 'html.parser')
            tag_links = [e.attrs['href'] for e in soup.select('a')]
            tag_body = re.match('^the-loai-([0-9a-z_]+)(\\.html)?$', tag).group(1)
            for tag_link in tag_links:
                if re.match(f'^/the-loai-[0-9]+-{tag_body}(\\.html)?$', tag_link):
                    return generate_response(custom_url(tag_link, page))


    @app.route('/reload')
    def backend_reload():
        return reload()

    requests.packages.urllib3.util.connection.HAS_IPV6 = piehtvn_config.use_ipv6

    logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(msg)s', level=logging.INFO)
    logging.info(f'listening on {piehtvn_config.host}:{piehtvn_config.port}')
    app.install(log_to_logger)
    app.run(host=piehtvn_config.host, port=piehtvn_config.port, quiet=True)


if __name__ == '__main__':
    main()
