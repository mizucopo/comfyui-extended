# comfyui-extended

ComfyUI の CUDA 対応 Docker イメージ。公開先は
[`mizucopo/comfyui-extended`](https://hub.docker.com/r/mizucopo/comfyui-extended) です。
モデルの重みはイメージに含めません。

## 構成

- ComfyUI: `v0.41.0`、commit `98cc0bf84b7cb1383654c5b402e7612d875d6d22`
- ベース: `pytorch/pytorch:2.14.1-cuda13.0-cudnn9-runtime`（Dockerfile で digest 固定）
- 作業ディレクトリ: `/opt/ComfyUI`
- 起動: `python main.py`。既定でポート `8188` を listen し、custom nodes と partner nodes を無効化します。
- 公開 CI: GitHub の標準 Linux x64 runner で `linux/amd64` イメージをビルドします。

通常の開発は Mac mini で行います。この CUDA ベースは Apple Silicon 向けの
ネイティブ実行環境ではありません。GPU 実行には NVIDIA Container Toolkit と
CUDA 13.0 に対応するホストドライバーが必要です。

## ビルドと検証

```sh
docker buildx build --check --platform linux/amd64 .
docker buildx build --platform linux/amd64 --load -t comfyui-extended:local .
docker run --rm comfyui-extended:local --cpu --help
```

最後のコマンドは GPU やモデルを使わない CLI 確認です。イメージのビルド自体には
大きな CUDA ベースと Python 依存のダウンロードが伴います。PR の
`docker-quality-checks` も公開せずに build checks とビルドを行います。

## 永続化と pc-setup との互換性

[`pc-setup` PR398](https://github.com/mizucopo/pc-setup/pull/398) の
commit `32c6cbe163c857d9e059aad84299251e44af3aad` と同じ上流 revision、
PyTorch ベース、依存導入方式、entrypoint を使用します。対応するマウント先は次のとおりです。

| 用途 | コンテナ内のパス |
| --- | --- |
| モデル | `/opt/ComfyUI/models`（読み取り専用） |
| Hugging Face cache | `/models/huggingface` |
| 入力・出力・ユーザー設定 | `/opt/ComfyUI/input`、`/opt/ComfyUI/output`、`/opt/ComfyUI/user` |
| custom nodes | `/opt/ComfyUI/custom_nodes`（読み取り専用、既定で無効） |

ホスト UID/GID で実行する場合、書き込み用 bind mount のディレクトリをそのユーザーの
所有で作成し、`HOME=/tmp` とします。PR398 と同じく
`/opt/ComfyUI/temp` と `/opt/ComfyUI/previews` に mode `1777` の tmpfs を指定してください。
外部アクセスの公開範囲は呼び出し元で管理し、ホストのポートを公開する場合は
必要に応じて `127.0.0.1:8188:8188` に限定します。

PR398 はまだローカル build を指定しているため、このイメージの公開だけでは
そのデプロイ先は切り替わりません。PR398 自体への変更はこのリポジトリには含みません。
GPU での生成やモデルの互換性は実機で別途確認します。

## Docker Hub への公開

Copier の標準 Docker Release workflow を使います。GitHub Actions の
`DOCKERHUB_TOKEN` は登録済みのものを利用し、ユーザー名は `mizucopo` です。
トークンの値をファイルへ書く必要はありません。

- PR・作業ブランチへの push は Docker Hub 公開を起動しません。
- 今回の Draft PR では公開を行わず、`release:*` ラベルを付けません。
- 将来の公開は、レビュー後に適切な `release:patch`、`release:minor`、
  `release:major` のいずれか一つを選び、main へ squash merge して行います。
- 最新のマージ済み PR に分類ラベルがない場合、main push や main を指定した
  手動実行でも公開はスキップされます。
- 完成した安定版の version tag と `latest` を公開します。GPU やモデルは不要ですが、
  認証の実動作と実際の公開は別の操作です。

分類の正本は [CONTRIBUTING.md](CONTRIBUTING.md)、採番・公開・復旧手順は
[docs/release.md](docs/release.md) を参照してください。

## テンプレート更新

`mizucopo/repo-template` の main を Copier で適用しています。
生成物は `.copier-answers.yml` で管理し、Dockerfile とこの README は製品側で所有します。
クリーンな専用ブランチで次を実行し、差分と競合を確認してください。

```sh
copier update --trust --defaults --vcs-ref HEAD
```
