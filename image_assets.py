import io
import pathlib

import requests
from PIL import Image


# ビルド内で元画像を共有する。公開するサムネイルとは分けて保存する。
SOURCE_IMAGES_DIR = pathlib.Path(".cache/pixiv-images")


def source_image_path(illust_id) -> pathlib.Path:
    return SOURCE_IMAGES_DIR / f"{illust_id}.img"


def download_source_image(illust_id, url: str) -> Image.Image:
    path = source_image_path(illust_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    # 今回の取得に失敗したとき、前回の元画像をSOMで使わないようにする。
    path.unlink(missing_ok=True)

    response = requests.get(
        url,
        headers={"Referer": "https://www.pixiv.net/", "User-Agent": "Mozilla/5.0"},
        timeout=20,
    )
    response.raise_for_status()
    with Image.open(io.BytesIO(response.content)) as source:
        image = source.convert("RGB")

    # 配信されたバイト列をそのまま保存し、再エンコードを避ける。
    path.write_bytes(response.content)
    return image
