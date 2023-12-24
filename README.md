# PieHTVN
HentaiVN scraper & simple API

## Backend
```shell
python backend.py
```

## API

<details>
<summary><code>/search</code></summary>

* Parameters:
  * `query`: search query, required
  * `pages`: page count, default to 1
* Return: dictionary with page number as the key and a list of doujinshis as the value

[`/search?query=genshin&pages=2`](https://paste.ee/p/xFB5t)

</details>
<br>

<details>
<summary><code>/get-chapters</code></summary>

* Parameters:
  * `url`: url of the doujinshi as returned by `search`
* Return: list of chapters

[`/get-chapters?url=13549-doc-truyen-traditional-job-of-washing-girls-body`](https://paste.ee/p/Afnme)
</details>
<br>

<details>
<summary><code>/get-metadata</code></summary>

* Parameters:
  * `url`: url of the doujinshi as returned by `search`
* Return: metadata about the doujinshi

[`/get-metadata?url=13549-doc-truyen-traditional-job-of-washing-girls-body`](https://paste.ee/p/a9rYB)
</details>
<br>

<details>
<summary><code>/get-images</code></summary>

* Parameters:
  * `url`: url of the chapter as returned by `get-chapters`
* Return: list of image URLs

[`/get-images?url=34611-64188-xem-truyen-sexual-manners-basics-and-principles-chap-1`](https://paste.ee/p/corus)
</details>
<br>

<details>
<summary><code>/download-image</code></summary>

* Parameters:
  * `url`: url of the image as returned by `get-images`
* Return: the image (duh)

</details>

## TODO
* remove duplicate results in search/custom
* add endpoints for character, author, translator, category, ...
* actually finish this readme