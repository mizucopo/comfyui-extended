# comfyui-extended

ComfyUI の CUDA 対応 Docker イメージです。モデルの重みは含みません。

## 必要条件

- Linux amd64、NVIDIA Container Toolkit、CUDA 13.0 に対応する GPU ドライバー。
- ビルドには大きな CUDA ベースと Python 依存のダウンロードが必要です。
- Apple Silicon でのネイティブ GPU 実行には対応しません。

ComfyUI `v0.41.0`（`98cc0bf84b7cb1383654c5b402e7612d875d6d22`）と
`pytorch/pytorch:2.14.1-cuda13.0-cudnn9-runtime` を使用します。
ベースイメージの digest は Dockerfile で固定しています。

## ビルドと起動

```sh
docker buildx build --platform linux/amd64 --load -t comfyui-extended:local .
docker run --rm --gpus all -p 127.0.0.1:8188:8188 comfyui-extended:local
```

ブラウザーで `http://127.0.0.1:8188` を開きます。custom nodes と partner nodes は
既定で無効です。モデルや出力を保持するには、必要なデータをマウントしてください。

GPU やモデルを使わず CLI を確認する場合は、次を実行します。

```sh
docker run --rm comfyui-extended:local --cpu --help
```

## データの保存先

| 用途 | コンテナ内のパス |
| --- | --- |
| モデル | `/opt/ComfyUI/models`（読み取り専用を推奨） |
| Hugging Face cache | `/models/huggingface` |
| 入力・出力・ユーザー設定 | `/opt/ComfyUI/input`、`/opt/ComfyUI/output`、`/opt/ComfyUI/user` |
| custom nodes | `/opt/ComfyUI/custom_nodes`（既定で無効） |

任意の UID/GID で実行する場合は、データ保存先と一時領域に書き込み権限を設定してください。
`HOME` は `/tmp`、アプリの一時領域は `/opt/ComfyUI/temp` と `/opt/ComfyUI/previews` です。
GPU での生成やモデルの互換性は実機で別途確認してください。

## イメージの公開

Docker Hub の公開予定先は
[`mizucopo/comfyui-extended`](https://hub.docker.com/r/mizucopo/comfyui-extended) です。
公開手順は [docs/release.md](docs/release.md)、変更の分類は
[CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。
