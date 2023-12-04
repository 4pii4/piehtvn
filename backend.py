
import json5
from bottle import Bottle, request
from piehtvn import *


def main():
    app = Bottle()

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

        return json5.dumps(results, ensure_ascii=False, quote_keys=True)

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

        return json5.dumps(results, ensure_ascii=False, quote_keys=True)

    @app.route('/get-chapters/<url>')
    def backend_get_chapters(url):
        doc = Doc('', Image(''), [], url, DOMAIN)
        return json5.dumps([x.json() for x in doc.get_chapters()], ensure_ascii=False, quote_keys=True)

    @app.route('/get-images/<url>')
    def backend_get_images(url):
        chapter = Chapter('', url, datetime.now(), DOMAIN)
        return json5.dumps([image.json() for image in chapter.get_images()], ensure_ascii=False, quote_keys=True)

    app.run(host='0.0.0.0', port=7479, debug=True)


if __name__ == '__main__':
    main()
