
import json5
from bottle import Bottle, request, response
from piehtvn import *


def main():
    app = Bottle()

    def generate_response(obj):
        response.set_header("Access-Control-Allow-Origin", "*")
        response.content_type = 'application/json'
        return json5.dumps(obj, ensure_ascii=False, quote_keys=True)

    @app.route('/search')
    def backend_search():
        params = dict(request.query.decode())
        if 'query' not in params:
            return 'Missing query parameter'
        if 'page' not in params:
            params['page'] = 1
        query = params['query']
        pages = int(params['page'])

        results = search(query, pages)

        for result in results:
            results[result] = [x.json() for x in results[result]]

        return generate_response(results)

    @app.route('/custom/<url>')
    def backend_search(url):
        params = dict(request.query.decode())
        if 'page' not in params:
            params['page'] = 1
        pages = int(params['page'])

        url = f'https://{DOMAIN}/{url}'
        results = custom_url(url, pages)

        for result in results:
            results[result] = [x.json() for x in results[result]]

        return generate_response(results)

    @app.route('/get-chapters/<url>')
    def backend_get_chapters(url):
        doc = Doc('', Image(''), [], url, DOMAIN)
        return generate_response([x.json() for x in doc.get_chapters()])

    @app.route('/get-metadata/<url>')
    def backend_get_chapter_metadata(url):
        doc = Doc('', Image(''), [], url, DOMAIN)
        return generate_response(doc.get_metadata().json())

    @app.route('/get-images/<url>')
    def backend_get_images(url):
        chapter = Chapter('', url, 0, DOMAIN)
        return generate_response([image.json() for image in chapter.get_images()])

    app.run(host='0.0.0.0', port=7479, debug=True)


if __name__ == '__main__':
    main()
