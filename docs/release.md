# 採番・公開

## 自動公開

PR ではテスト・Docker build checks・Linux amd64 のビルドを行い、公開しません。
main への squash merge 後は `Docker Release` が自動で実行されます。
公開用ラベル、手動 dispatch、事前の GitHub Release 作成は不要です。

1. 最新 main の squash merge を確認し、版とイメージ改訂を採番する。
2. 採番 commit と Git タグを atomic push する。
3. その commit を checkout し、テスト・Docker build checks・実ビルドを行う。
4. 成功したイメージを Docker Hub の `mizucopo/comfyui-extended` へ公開する。
5. registry digest を検証し、GitHub Release を自動公開する。安定版は `latest` も更新する。

認証には既存の Actions secret `DOCKERHUB_TOKEN` と `GITHUB_TOKEN` を使います。
secret の値をファイルへ転記しないでください。main・タグへ通常の push が必要です。
権限や保護設定で拒否された場合は停止し、workflow で保護を回避しません。

## ComfyUI のバージョンとイメージ改訂

`version` は ComfyUI 公式タグの先頭の `v` を除いた値です。Dockerfile 冒頭の
`COMFYUI_VERSION` に同じ値を設定し、`COMFYUI_COMMIT` をそのタグの commit に揃えます。
ビルドは `refs/tags/v${COMFYUI_VERSION}` を取得して SHA を照合します。

新しい公式タグへ更新するときは、この3値を揃えて `revision` を空にします。
`.github/release.json` の `upstream-revision` 方式により、初回は `x.y.z`、
同じ版の改訂は `x.y.z-r1`、`x.y.z-r2` と進みます。`-r0` は省略します。
Git タグ・GitHub Release 名・Docker Hub タグは同じ値です。
上流 version を公開都合で増やすことはありません。

Dockerfile の更新入力は、冒頭に一度だけ値を宣言した `COMFYUI_VERSION`、
`COMFYUI_COMMIT`、`PYTORCH_IMAGE` です。ベースのみの更新では `PYTORCH_IMAGE` の
タグと digest を一緒に置換し、`version` と `revision` を保持します。
同じ上流版の変更は、公開時に次の revision を自動採番します。
既存タグとの衝突も、上流版を変えず空いている revision へ進めます。
上流自体が prerelease の場合は `latest` を更新しません。

## 重複実行と復旧

workflow 全体を `release-main` の concurrency group で直列化します。
同じ run の再実行は、採番済み commit とタグを再利用します。
別 run でも新しいマージ済み PR がなければ採番・公開をスキップします。
main の更新が競合したときは最大3回再計算します。

公開済みイメージは上書きしません。既存タグの所有 commit と digest を確認し、
同じ run の部分公開を再開します。全 job の成功後に digest の証拠を Release へ保存し、
その版の一時的な image ownership branch だけを削除します。
古い run の復旧で新しい `latest` を巻き戻すことはありません。

| 状態 | 対応 |
| --- | --- |
| テスト・ビルド失敗 | 原因を確認し、元 run を再実行。コード修正は新しい PR で取り込む。 |
| 部分公開・通信失敗 | 元 run を再実行して不足分を継続する。認証や照会の失敗を「未公開」と扱わない。 |
| マージ証拠・権限・公開状態の不整合 | 停止して原因を確認する。タグ・イメージ・履歴を上書きしない。 |

失敗しても採番 commit とタグは保持します。再実行に新しいラベルや dispatch は不要です。
Copier 更新には通常の three-way update を使い、製品側の自動公開と版・revision の規則を維持してください。
