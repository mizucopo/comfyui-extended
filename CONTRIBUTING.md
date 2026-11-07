# コントリビューション

非 main branch で変更し、テスト・lint の結果を PR 本文に記載してください。
通常の変更は squash merge で main へ取り込みます。

## 公開

main へのマージは Docker Hub への公開を伴います。ラベル・手動 dispatch・
事前の GitHub Release 作成は不要です。PR ではテストとイメージのビルドだけを行い、
マージ後に同じ検証を通過してから `mizucopo/comfyui-extended` へ公開します。
Dependabot の PR も同じ扱いです。

文書のみ・テストのみの PR も公開対象です。`.github/release.json` の
`publication.release_paths` は公開入力の宣言であり、差分や分類ラベルで公開を
抑止しません。新しい squash-merged PR がなければ新しい番号は作りません。

上流の ComfyUI version を保ち、同版の変更はイメージの revision だけを自動採番します。
版の更新方法と失敗時の復旧は [docs/release.md](docs/release.md) を参照してください。
マージや実際の公開を行う操作には、その操作への依頼が必要です。
