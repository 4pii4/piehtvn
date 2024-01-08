import dataclasses
import json

from bottle import Bottle, request, response

from piehtvn import *


def main():
    app = Bottle()
    with open('config.json') as f:
        config = json.loads(f.read())

    def generate_response(obj):
        class EnhancedJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if dataclasses.is_dataclass(o):
                    return dataclasses.asdict(o)
                return super().default(o)

        response.set_header("Access-Control-Allow-Origin", "*")
        response.content_type = 'application/json'
        return json.dumps(obj, ensure_ascii=False, cls=EnhancedJSONEncoder)

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

    app.run(host=config['host'], port=config['port'], debug=config['debug'])


if __name__ == '__main__':
    main()
