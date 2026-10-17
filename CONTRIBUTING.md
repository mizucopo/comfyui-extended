# コントリビューション

非 main branch で変更し、テスト・lint の結果を PR 本文に記載してください。
通常の変更は squash merge で main へ取り込みます。

## 公開

main へのマージは Docker Hub への公開を伴います。ラベル・手動 dispatch・
事前の GitHub Release 作成は不要です。PR ではテストとイメージのビルドだけを行い、
マージ後に同じ検証を通過してから `mizucopo/comfyui-extended` へ公開します。
Dependabot の PR も同じ扱いです。

上流の ComfyUI version を保ち、同版の変更はイメージの revision だけを自動採番します。
版の更新方法と失敗時の復旧は [docs/release.md](docs/release.md) を参照してください。
マージや実際の公開を行う操作には、その操作への依頼が必要です。
