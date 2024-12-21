import asyncio

from httpx import AsyncClient
from loguru import logger

DOWNLOADS_FOLDER = "downloaded/"

headers = {
    "Host": "image-cdn.hotleaks.tv",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Priority": "u=0, i",
}

headers_api = {
    "Host": "hotleaks.tv",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://hotleaks.tv/hannahowo/photo",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "TE": "trailers",
    "X-Requested-With": "XMLHttpRequest",
}


class EmptyPhotos(Exception):
    pass


async def download_photo(client: AsyncClient, url: str):
    response = await client.get(url, headers=headers)

    filename = url.split("/")[-1]

    with open(DOWNLOADS_FOLDER + filename, "wb") as fp:
        fp.write(response.content)


async def get_page_photos(client: AsyncClient, url: str, page: int = 1) -> list[str]:
    response = await client.get(
        url,
        headers=headers_api,
        params={"page": page, "type": "photos", "order": 0},
    )

    json = response.json()

    if isinstance(json, list):
        logger.debug("got {} photos", len(json))

        photos = list(map(lambda i: i["player"], json))

        if not photos:
            raise EmptyPhotos

        return photos
    else:
        logger.warning("Wrong page api response!")

    return []


async def main():
    download_url = input("Insert download link (ex: https://hotleaks.tv/hannahowo): ")

    if not download_url.startswith("https://hotleaks.tv/"):
        logger.error("Wrong URL!")
        return

    if download_url.endswith("/"):
        download_url = download_url[:-1]

    if download_url.endswith("/photo") or download_url.endswith("/video"):
        download_url = download_url[:-6]

    client = AsyncClient(http2=True)

    working = True
    page = 1

    photo_count = 0

    while working:
        try:
            photos = await get_page_photos(client, download_url, page)

            photo_count += len(photos)

            for photo in photos:
                await download_photo(client, photo)

                await asyncio.sleep(0.05)
        except EmptyPhotos:
            logger.info(
                "Download finished, was {} pages with {} photos!", page, photo_count
            )
            working = False

        page += 1


if __name__ == "__main__":
    asyncio.run(main())
