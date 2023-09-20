# PieHtvn
HentaiVN scraper & simple API

## Server
```shell
python backend.py
```

## API Usage

### `search`
* Parameters:
  * `query`: search query, required
  * `page`: page count, default to 1
* Return: dictionary with page number as the key and a list of documents as the value

<details>
<summary>Example with only <code>query</code> parameter</summary>

```shell
curl localhost:7479/search?query=traditional
```
```json5
{'1': [{'cover': 'https://t.htvncdn.net/images/300/traditional-job-of-washing-girls-body.jpg',
        'domain': 'hentaivn.autos',
        'title': "Traditional Job of Washing Girls' Body",
        'url': '/13549-doc-truyen-traditional-job-of-washing-girls-body.html'}]}
```

</details>

<details>
<summary>Example with <code>query</code> and <code>page</code> parameters</summary>

```shell
curl localhost:7479/search?query=genshin&page=2
```
```json5
{'1': [{'cover': 'https://t.htvncdn.net/images/300/1694259898-q1.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Sếch với thủy thần',
        'url': '/34620-doc-truyen-sech-voi-thuy-than.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1694666396-1.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Furina ngu ngốc.',
        'url': '/34701-doc-truyen-furina-ngu-ngoc-.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1692804583-ba.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Làm gì có vùng đất cạm bẫy dục vọng chưa được khám phá',
        'url': '/34459-doc-truyen-lam-gi-co-vung-dat-cam-bay-duc-vong-chua-duoc-kham-pha.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1694171852-1.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Boku, Hontou wa Mona no Koto ga Suki nanda (Genshin Impact)',
        'url': '/34608-doc-truyen-boku-hontou-wa-mona-no-koto-ga-suki-nanda-genshin-impact.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1694020907-ba.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Eula & Nhà lữ hành',
        'url': '/34591-doc-truyen-eula-nha-lu-hanh.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1693750365-ba.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Thuỷ thần ngốc nghếch',
        'url': '/34557-doc-truyen-thuy-than-ngoc-nghech.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1686324088-01.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Lễ hội mùa xuân Mondstadt',
        'url': '/33915-doc-truyen-le-hoi-mua-xuan-mondstadt.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1644168345-01.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Shoufugai - Mona & Lisa',
        'url': '/29194-doc-truyen-shoufugai-mona-lisa.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1676310786-cover.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Giấc mơ băng giá',
        'url': '/33032-doc-truyen-giac-mo-bang-gia.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1692192219-131.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Dàn harem của Timmie. (Genshin Impact)',
        'url': '/33130-doc-truyen-dan-harem-cua-timmie-genshin-impact.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1692031492-rosac_001.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Am I A Saint Or Sinner?',
        'url': '/34371-doc-truyen-am-i-a-saint-or-sinner.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1678116245-0.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Do You Really Like Me?',
        'url': '/33178-doc-truyen-do-you-really-like-me.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1691846256-1.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Trang trại Nguyên Thần',
        'url': '/34355-doc-truyen-trang-trai-nguyen-than.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1686201298-ba.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Món Quà Của Thất Tinh',
        'url': '/23613-doc-truyen-mon-qua-cua-that-tinh.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1681306864-ba.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Tất cả vì nghệ thuật',
        'url': '/33487-doc-truyen-tat-ca-vi-nghe-thuat.html'}],
 '2': [{'cover': 'https://t.htvncdn.net/images/300/1680762286-01.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Cuộc thi ẩm thực trung thu của Xiangling',
        'url': '/33416-doc-truyen-cuoc-thi-am-thuc-trung-thu-cua-xiangling.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1691004877-01.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Warming to the Core',
        'url': '/34278-doc-truyen-warming-to-the-core.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1690713243-3.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Play With Klee New Outfit',
        'url': '/34256-doc-truyen-play-with-klee-new-outfit.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1690079901-layla_hypnosis_001.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Laylas Late Night Training Session',
        'url': '/34206-doc-truyen-laylas-late-night-training-session.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1689877968-106868602_p0.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Master Jeans Little Secret',
        'url': '/34194-doc-truyen-master-jeans-little-secret.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1689866790-01.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Oshiri ni Ireru to Kimochiyokute Tamaranai Bow tte nanda? (なぽ氏)',
        'url': '/34192-doc-truyen-oshiri-ni-ireru-to-kimochiyokute-tamaranai-bow-tte-nanda-なぽ氏.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1689841695-1.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Deisui Shita Yae Miko ni Warui Koto o Suru Hanashi (Genshin Impact)',
        'url': '/34189-doc-truyen-deisui-shita-yae-miko-ni-warui-koto-o-suru-hanashi-genshin-impact.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1683737545-cover.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Lôi thần đi thị sát',
        'url': '/33664-doc-truyen-loi-than-di-thi-sat.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1680792360-ba.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Bí mật của Ayaka',
        'url': '/33423-doc-truyen-bi-mat-cua-ayaka.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1688479260-1.jpg',
        'domain': 'hentaivn.autos',
        'title': "Nilou 'sum suê' (Genshin Impact)",
        'url': '/34085-doc-truyen-nilou-sum-sue-genshin-impact.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1680920858-1copy.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Genshin NTR: Keqing (Genshin Impact)',
        'url': '/33417-doc-truyen-genshin-ntr-keqing-genshin-impact.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1687107631-9.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Paimon Ecchi Manga',
        'url': '/33977-doc-truyen-paimon-ecchi-manga.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1686416961-1.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Ganyu-chan ga Shigoto to Seiyoku Shori o Otetsudai suru Hon.',
        'url': '/33921-doc-truyen-ganyu-chan-ga-shigoto-to-seiyoku-shori-o-otetsudai-suru-hon-.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1686221767-02.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Tổng hợp truyện ngắn của StrongBana',
        'url': '/32593-doc-truyen-tong-hop-truyen-ngan-cua-strongbana.html'},
       {'cover': 'https://t.htvncdn.net/images/300/1686211630-1.jpg',
        'domain': 'hentaivn.autos',
        'title': 'Columbina',
        'url': '/33901-doc-truyen-columbina.html'}]}
```

</details>

<br>

### `get-chapters/<url>`
* Parameters:
  * `url`: url of the document as returned by `search`
* Return: list of chapters

<details>
<summary>Example</summary>

```shell
curl localhost:7479/get-chapters/13549-doc-truyen-traditional-job-of-washing-girls-body.html
```
```json5
[{'domain': 'hentaivn.autos',
  'time': '10/09/2023',
  'title': 'Chap 8 - END',
  'url': '/34611-64221-xem-truyen-34611-doc-truyen-sexual-manners-basics-and-principles.html-chap-8-end.html'},
 {'domain': 'hentaivn.autos',
  'time': '10/09/2023',
  'title': 'Chap 7',
  'url': '/34611-64220-xem-truyen-34611-doc-truyen-sexual-manners-basics-and-principles.html-chap-7.html'},
 {'domain': 'hentaivn.autos',
  'time': '10/09/2023',
  'title': 'Chap 6',
  'url': '/34611-64219-xem-truyen-34611-doc-truyen-sexual-manners-basics-and-principles.html-chap-6.html'},
 {'domain': 'hentaivn.autos',
  'time': '10/09/2023',
  'title': 'Chap 5',
  'url': '/34611-64218-xem-truyen-34611-doc-truyen-sexual-manners-basics-and-principles.html-chap-5.html'},
 {'domain': 'hentaivn.autos',
  'time': '08/09/2023',
  'title': 'Chap 4',
  'url': '/34611-64191-xem-truyen-34611-doc-truyen-sexual-manners-basics-and-principles.html-chap-4.html'},
 {'domain': 'hentaivn.autos',
  'time': '08/09/2023',
  'title': 'Chap 3',
  'url': '/34611-64190-xem-truyen-34611-doc-truyen-sexual-manners-basics-and-principles.html-chap-3.html'},
 {'domain': 'hentaivn.autos',
  'time': '08/09/2023',
  'title': 'Chap 2',
  'url': '/34611-64189-xem-truyen-34611-doc-truyen-sexual-manners-basics-and-principles.html-chap-2.html'},
 {'domain': 'hentaivn.autos',
  'time': '08/09/2023',
  'title': 'Chap 1',
  'url': '/34611-64188-xem-truyen-34611-doc-truyen-sexual-manners-basics-and-principles.html-chap-1.html'}]
```
</details>

<br>

### `get-images/<url>`
* Parameters:
  * `url`: url of the chapter as returned by `get-chapters`
* Return: list of image URLs

<details>
<summary>Example</summary>

```shell
curl localhost:7479/get-images/34611-64188-xem-truyen-sexual-manners-basics-and-principles-chap-1.html
```
```json5
['https://ULGREEDFoWs.hentaivn.autos/i&m+a-IIJFGCFWDFqZavg+e!s+1200/2023/09/08/1694185917-pic01.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-QQcgfeBFrecQg+e!s+1200/2023/09/08/1694185919-pic02.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-WWexcdfGRexcXzqg+e!s+1200/2023/09/08/1694185920-pic03.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-NNdfvrecewg+e!s+1200/2023/09/08/1694185921-pic04.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-GBfdedsdrg+e!s+1200/2023/09/08/1694185921-pic05.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-NNdfvrecewg+e!s+1200/2023/09/08/1694185922-pic06.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-NZu7ULbbqwoVg+e!s+1200/2023/09/08/1694185923-pic07.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-FRiYTGFGerfspPg+e!s+1200/2023/09/08/1694185924-pic08.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-NNdfvrecewg+e!s+1200/2023/09/08/1694185924-pic09.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-NNdfvrecewg+e!s+1200/2023/09/08/1694185926-pic10.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-FRiYTGFGerfspPg+e!s+1200/2023/09/08/1694185927-pic11.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-YtrrfdvIYHrtfRg+e!s+1200/2023/09/08/1694185927-pic12.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-YtrrfdvIYHrtfRg+e!s+1200/2023/09/08/1694185928-pic13.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-YGfeffsdsGDrFDgqg+e!s+1200/2023/09/08/1694185929-pic14.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-IIJFGCFWDFqZavg+e!s+1200/2023/09/08/1694185930-pic15.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-HTYTgfgeFGreWg+e!s+1200/2023/09/08/1694185931-pic16.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-IIJFGCFWDFqZavg+e!s+1200/2023/09/08/1694185931-pic17.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-OOrdOOFGTRFwdeSXg+e!s+1200/2023/09/08/1694185932-pic18.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-PPPOHUerwrefFEwdrg+e!s+1200/2023/09/08/1694185933-pic19.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-IIJFGCFWDFqZavg+e!s+1200/2023/09/08/1694185934-pic20.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-ULGREFDFoVsg+e!s+1200/2023/09/08/1694185935-pic21.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-Dswwxxhgcg+e!s+1200/2023/09/08/1694185937-pic22.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-YGfeffsdsGDrFDgqg+e!s+1200/2023/09/08/1694185938-pic23.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-ZZXzsdasTGRtreCg+e!s+1200/2023/09/08/1694185939-pic24.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-QQsaxaXKjbjg+e!s+1200/2023/09/08/1694185940-pic25.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-YtrrfdvIYHrtfRg+e!s+1200/2023/09/08/1694185941-pic26.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-WQEwxhjTGERetIvfBQg+e!s+1200/2023/09/08/1694185941-pic27.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-ZZXzsdasTGRtreCg+e!s+1200/2023/09/08/1694185942-pic28.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-HTYTgfgeFGreWg+e!s+1200/2023/09/08/1694185943-pic29.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-YtrrfdvIYHrtfRg+e!s+1200/2023/09/08/1694185944-pic30.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-NNdfvrecewg+e!s+1200/2023/09/08/1694185945-pic31.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-YtrrfdvIYHrtfRg+e!s+1200/2023/09/08/1694185946-pic32.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-WQEwxhjTGERetIvfBQg+e!s+1200/2023/09/08/1694185947-pic33.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-ZZXzsdasTGRtreCg+e!s+1200/2023/09/08/1694185948-pic34.jpg',
 'https://ULGREEDFoWs.hentaivn.autos/i&m+a-WWexcdfGRexcXzqg+e!s+1200/2023/09/08/1694185948-pic35.jpg']
```
</details>

## TODO
* remove duplicate results in search/custom
* fix bugs with unicode urls
* actually finish this readme