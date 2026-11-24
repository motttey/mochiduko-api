# mochiduko-api
最新のイラスト情報などをJSON出力する

## refresh tokenの取得
PixivPyを使ってAPIからデータを取得するにはトークンが必要。

[リフレッシュトークンを取得するスクリプト](https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde) を実行し、帰ってきたトークンを環境変数にセットする。

## データの生成

`python api.py` の後に `python prep_som_hexbin.py` を実行する。
元画像は `api.py` で一度だけ取得して `.cache/pixiv-images/` に保存し、
t-SNE用のPNG、表示用のWebP、SOMの特徴抽出に共用する。
SOM用のJPEGも `public/thumbs/` に出力する。元画像は公開しない。

SOMは14×14のグリッドで、学習回数は `min(4000, 100 × 画像数)` とする。

テストは依存ライブラリをインストールした環境で
`python -m unittest discover -s tests` を実行する。
