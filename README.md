# comfyui-extended

ComfyUI の CUDA 対応 Docker イメージです。モデルの重みは含みません。

## 必要条件

- Linux amd64、NVIDIA Container Toolkit、ベースイメージの CUDA に対応する GPU ドライバー。
- ビルドには大きな CUDA ベースと Python 依存のダウンロードが必要です。
- Apple Silicon でのネイティブ GPU 実行には対応しません。

ComfyUI の[公式タグ](https://github.com/Comfy-Org/ComfyUI/tags)は `vx.y.z` 形式です。
使用する版は [version](version)、PyTorch/CUDA ベースと固定 digest は
[Dockerfile](Dockerfile) を確認してください。

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

Docker Hub の公開先は
[`mizucopo/comfyui-extended`](https://hub.docker.com/r/mizucopo/comfyui-extended) です。
main への squash merge 後、テスト・ビルドに成功すれば自動公開されます。
ラベルや手動実行は不要です。詳細は [docs/release.md](docs/release.md) を参照してください。

`version` は上流タグの `v` を除いた値です。イメージ・Git タグ・Release 名は
初回が `x.y.z`、同じ上流版の改訂が `x.y.z-r1` 以降になります。
上流版の更新時は `revision` を空にし、同じ版の改訂番号は公開時に自動採番します。
