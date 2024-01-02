import requests

from piehtvn import Chapter, DOMAIN, Image

s = requests.Session()

for img in Chapter(None, '33837-64689-xem-truyen-netorimura-chap-4ket-thuc.html', None, DOMAIN).get_images():
    req = Image(img).get_request().prepare()
    res = s.send(req)
    print(img, len(res.content))