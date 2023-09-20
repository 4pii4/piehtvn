from bottle import Bottle, request
from piehtvn import *
from pprint import pformat


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

        for k in results:
            results[k] = [x.json() for x in results[k]]

        results = {str(k): v for k, v in results.items()}
        return pformat(results)

    @app.route('/custom/<url>')
    def backend_search(url):
        params = dict(request.query.decode())
        if 'page' not in params:
            params['page'] = 1
        pages = int(params['page'])

        url = f'https://{DOMAIN}/{url}'
        results = custom_url(url, pages)

        for k in results:
            results[k] = [x.json() for x in results[k]]

        results = {str(k): v for k, v in results.items()}

        return pformat(results)

    @app.route('/get-chapters/<url>')
    def backend_get_chapters(url):
        d = Doc('', Image(''), url, DOMAIN)
        chapters = d.get_chapters()
        return pformat([x.json() for x in chapters])

    @app.route('/get-images/<url>')
    def backend_get_images(url):
        c = Chapter('', url, datetime.now(), DOMAIN)
        images = c.get_images()
        return pformat([x.json() for x in images])

    app.run(host='0.0.0.0', port=7479, debug=True)


if __name__ == '__main__':
    main()
