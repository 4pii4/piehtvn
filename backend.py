import dataclasses
import json
import logging
import platform
import subprocess
from datetime import timedelta
from functools import wraps

from bottle import Bottle, request, response

from piehtvn import *


def main():
    start_time = time.time()

    output = subprocess.check_output(['whoami']).decode('utf-8')
    commitid = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8')
    commitid_short = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8')
    if platform.system() == 'Windows':
        platformwin = platform.win32_ver()
        osver = 'Windows version ' + platformwin[1]
    else:
        osver = subprocess.check_output(['uname', '-s']).decode('utf-8') + ' ' + subprocess.check_output(
            ['uname', '-r']).decode('utf-8')

    app = Bottle()

    with open('config.json') as f:
        config = json.loads(f.read())

    def log_to_logger(fn):
        @wraps(fn)
        def _log_to_logger(*args, **kwargs):
            actual_response = fn(*args, **kwargs)
            # modify this to log exactly what you need:
            logging.info('%s %s %s %s' % (request.remote_addr,
                                          request.method,
                                          request.url,
                                          response.status,))
            return actual_response

        return _log_to_logger

    def generate_response(obj):
        class EnhancedJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if dataclasses.is_dataclass(o):
                    return dataclasses.asdict(o)
                return super().default(o)

        response.set_header("Access-Control-Allow-Origin", "*")
        response.content_type = 'application/json'
        return json.dumps(obj, ensure_ascii=False, cls=EnhancedJSONEncoder)

    def uptime_calculate():
        return str(timedelta(seconds=round(time.time()) - round(start_time)))

    @app.route('/')
    def root():
        return (('<title>Welcome to PieHTVN</title><h1>Welcome to <a '
                 'href="https://github.com/4pii4/piehtvn">PieHTVN</a></h1><p>Backend is running as <b>') + output +
                '</b> on <b>' + osver + '</b></p>\n<p>Current git commit: <b><a '
                                        'href="https://github.com/4pii4/piehtvn/commit/' + commitid + '">' +
                commitid_short + '</a></b></p>\n<p>Current pointed domain: <b>' + Domain.get_domain() +
                '</b></p>\nUptime: <b>' + uptime_calculate() + '</b>')

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

    @app.route('/custom')
    def backend_search():
        if request.query.url is None:
            return 'missing url parameter'

        pages = int(request.query.pages or 1)
        url = f'https://{Domain.get_domain()}/{request.query.url}'

        return generate_response(custom_url(url, pages))

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
        response.set_header("Access-Control-Allow-Origin", "*")
        response.content_type = f'image/{img.url.split(".")[-1]}'
        with requests.Session() as session:
            resp = session.send(img.get_request().prepare())
        return resp.content

    @app.route('/reload')
    def backend_reload():
        return reload()

    @app.route('/domain')
    def backend_domain():
        return Domain.get_domain()

    logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(msg)s', level=logging.INFO)
    logging.info(f"listening on {config['host']}:{config['port']}")
    app.install(log_to_logger)
    app.run(host=config['host'], port=config['port'], quiet=True)


if __name__ == '__main__':
    main()
