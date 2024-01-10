import dataclasses
import json
import logging
from functools import wraps
import datetime

from bottle import Bottle, request, response

from piehtvn import *


def main():
    app = Bottle()
    logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(msg)s', level=logging.INFO)

    with open('config.json') as f:
        config = json.loads(f.read())

    def log_to_logger(fn):
        '''
        Wrap a Bottle request so that a log line is emitted after it's handled.
        (This decorator can be extended to take the desired logger as a param.)
        '''
        @wraps(fn)
        def _log_to_logger(*args, **kwargs):
            actual_response = fn(*args, **kwargs)
            # modify this to log exactly what you need:
            logging.info('%s %s %s %s' % (request.remote_addr,
                                            request.method,
                                            request.url,
                                            response.status, ))
            return actual_response
        return _log_to_logger
    app.install(log_to_logger)

    def generate_response(obj):
        class EnhancedJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if dataclasses.is_dataclass(o):
                    return dataclasses.asdict(o)
                return super().default(o)

        response.set_header("Access-Control-Allow-Origin", "*")
        response.content_type = 'application/json'
        return json.dumps(obj, ensure_ascii=False, cls=EnhancedJSONEncoder)

    @app.route('/')
    def root():
        return 'proper index page coming soon'

    @app.route('/homepage')
    def backend_homepage():
        return generate_response(homepage())


    @app.route('/search')
    def backend_search():
        if request.query.query is None:
            return 'missing query parameter'
        query = request.query.query
        pages = int(request.query.pages or 1)

        return generate_response(search(query, pages))

    @app.route('/custom')
    def backend_search():
        if request.query.url is None:
            return 'missing url parameter'

        pages = int(request.query.pages or 1)
        url = f'https://{DOMAIN}/{request.query.url}'

        return generate_response(custom_url(url, pages))

    # noinspection PyTypeChecker
    @app.route('/get-chapters')
    def backend_get_chapters():
        doc = Doc(None, request.query.url, None, None, DOMAIN)
        return generate_response(doc.get_chapters())

    # noinspection PyTypeChecker
    @app.route('/get-metadata')
    def backend_get_chapter_metadata():
        doc = Doc(None, request.query.url.removeprefix('.html') + '.html', None, None, DOMAIN)
        return generate_response(doc.get_metadata())

    # noinspection PyTypeChecker
    @app.route('/get-images')
    def backend_get_images():
        chapter = Chapter(None, request.query.url.removeprefix('.html') + '.html', None, DOMAIN)
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

    logging.info(f"listening on {config['host']}:{config['port']}")

    app.run(host=config['host'], port=config['port'], quiet=True)


if __name__ == '__main__':
    main()
