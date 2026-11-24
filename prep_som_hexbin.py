import json, pathlib
from typing import List, Dict
import numpy as np
from PIL import Image
from tqdm import tqdm

import torch
import torchvision.transforms as T
from torchvision.models import resnet50, ResNet50_Weights

# SOM
from minisom import MiniSom
from sklearn.preprocessing import StandardScaler
from image_assets import source_image_path

OUT_DIR = pathlib.Path("public")
THUMBS_DIR = OUT_DIR / "thumbs"
DATA_JSON = OUT_DIR / "som_data.json"

THUMB_SIZE = 100
SOM_W, SOM_H = 14, 14  # SOMのグリッドサイズ（大きくするとより密に並ぶ）
SOM_MAX_ITERATIONS = 4000

# -------- 画像→埋め込みベクトル --------
def build_feature_extractor():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    weights = ResNet50_Weights.DEFAULT
    model = resnet50(weights=weights)
    model.eval().to(device)
    # 平均プーリング層直前まで取得するフック
    layer_output = {}

    def hook_fn(_module, _inp, out):
        # out: (N, 2048, 7, 7) -> GlobalAvgPool で (N, 2048)
        gap = out.mean(dim=[2,3])  # (N, 2048)
        layer_output['feat'] = gap.detach().cpu().numpy()

    model.layer4.register_forward_hook(hook_fn)

    transform = T.Compose([
        T.Resize(128),
        T.CenterCrop(11),
        T.ToTensor(),
        T.Normalize(mean=weights.transforms().mean, std=weights.transforms().std),
    ])

    def extract(img: Image.Image) -> np.ndarray:
        with torch.no_grad():
            x = transform(img).unsqueeze(0).to(device)
            _ = model(x)
            feat = layer_output['feat'][0]
            return feat

    return extract

def main():
    with open('public/each_illusts.json') as f:
        items: List[Dict] = json.load(f)

    THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    extractor = build_feature_extractor()
    features = []
    outputs = []

    for it in tqdm(items, desc="embed"):
        try:
            # api.pyで一度だけ取得した元画像を使い、再ダウンロードしない。
            with Image.open(source_image_path(it["id"])) as source:
                img = source.convert("RGB")
        except OSError as e:
            print(f"skip {it.get('id')} ({e})")
            continue

        # サムネ保存（ローカル相対パスを可視化で参照）
        thumb_path = THUMBS_DIR / f"{it['id']}.jpg"
        img_thumb = img.copy()
        img_thumb.thumbnail((THUMB_SIZE, THUMB_SIZE))
        img_thumb.save(thumb_path, "JPEG", quality=90)

        # 特徴抽出
        feat = extractor(img)
        features.append(feat)
        outputs.append({
            "id": it["id"],
            "title": it["title"],
            "date": it["date"],
            "view": it.get("view"),
            "bookmark": it.get("bookmark"),
            "comments": it.get("comments"),
            "tags": [t["name"] for t in it.get("tags", [])],
            "thumb": f"./thumbs/{it['id']}.jpg"
        })

    if not features:
        raise RuntimeError("no images embedded")

    X = np.vstack(features).astype(np.float32)
    X = StandardScaler().fit_transform(X)

    # SOM 学習
    som = MiniSom(
        SOM_H,
        SOM_W,
        X.shape[1],
        sigma=1.0,
        learning_rate=0.5,
        neighborhood_function='gaussian'
    )

    som.random_weights_init(X)
    som.train_random(X, num_iteration=min(SOM_MAX_ITERATIONS, 100 * len(X)))

    # BMU（勝者ニューロン）座標を取り出し→可視化座標にマッピング
    coords = []
    for _i, x in enumerate(X):
        r, c = som.winner(x)  # (row, col) 0-based
        # [0,1] に正規化
        u = (c + 0.5) / SOM_W
        v = (r + 0.5) / SOM_H
        coords.append((u, v))

    for out, (u, v) in zip(outputs, coords):
        out["u"] = float(u)
        out["v"] = float(v)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(outputs, f, ensure_ascii=False, indent=2)

    print(f"wrote: {DATA_JSON}  (thumbs in {THUMBS_DIR})")

if __name__ == "__main__":
    main()
