# 土地事業の資金収支

Python / Streamlit / Snowflakeを使う、架空3案件・24か月の公開用ポートフォリオ。
物流施設の土地を取得・企画して開発ファンドへ売却する自社の資金繰りです。
実企業の財務情報は含みません。売上・利益と借入金を混同しません。

## ローカルで確認

Python 3.12を推奨。

```sh
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
streamlit run streamlit_app.py
```

初期状態は **デモモード（Snowflake未接続）**。ローカルの架空データを表示します。
標準・売却3か月遅延・カスタムの切替、案件選択、月別入出金、現金残高、NPV、明細CSVを利用できます。
初期現金は2026-10-01時点1億2千万円、実績基準日は2026-10-28。通貨は円、日付は日本業務日として扱います。
標準シナリオの24か月後現金は201,550,000円。3か月遅延は追加利息1,725,000円です。

## Snowflake接続

1. 所有者がSnowflakeへログインする。既存Warehouse/試用クレジットを確認する。
2. `sql/01_schema.sql` → `02_seed.sql` → `03_views.sql` を順に実行する。`00_warehouse_optional.sql` は必要時・承認後のみ。
3. 案件3件、入出金54件、実績2件をSQLで確認する。シードはMERGEで再実行しても増えません。
4. 公開アプリ専用の鍵ペア認証ユーザーと読取専用ロールを別途承認のうえ設定する。必要権限はWarehouseのUSAGE、DB/スキーマのUSAGE、`MART.PUBLIC_PROJECTS` と `MART.PUBLIC_CASH_EVENTS` のSELECTのみ。RAWへの権限は不要。
5. `.streamlit/secrets.toml.example` を参考に **ホストのSecrets画面** に設定し、`app.mode = "snowflake"` とする。ローカルならgitignoreされた `.streamlit/secrets.toml` に保存。
6. Snowflakeモードで表示されることと、QUERY_HISTORYのQUERY_TAG `snowflakesample_public_readonly` を確認する。

管理者パスワード、Googleログイン情報、秘密鍵をGitHubやブラウザ側コードへ入れないでください。
SDKの不要なクラウドメタデータ探索は公式設定で無効にしています。アプリは固定2クエリのみをサーバーで実行し、結果を最大5分キャッシュします。接続失敗時は停止し、デモへ自動切替しません。
無料ホスティングでもSnowflakeの利用クレジットは別です。自動有料化は行いません。

## 匿名公開

Streamlit in Snowflakeの認証画面を一般公開するのではなく、**外部のStreamlitホスト → Snowflake** の構成にします。
候補はStreamlit Community Cloud（無料）。非公開GitHubリポジトリのまま、アプリの閲覧設定だけpublicにできます。

- ホストにログインしGitHub接続を許可（必要な連携権限は所有者が承認）。
- `onopod/snowflakesample`, branch `main`, entrypoint `streamlit_app.py`, Python 3.12を指定。
- Secretsを設定しデプロイ。公開範囲をpublicにする。リポジトリ自体を公開する必要はありません。
- ログアウト/シークレットブラウザで、ログイン不要・グラフ・フィルター・CSV・遅延シナリオを検証する。

**コードを配置しただけでは公開完了ではありません。** 公開URLとSnowflake接続の実測確認は別々に記録します。

## 計算範囲

- 1明細に予定と実績を持ち、実績を優先。部分決済は別明細として入力する。
- 過去の未決済予定は基準日翌日に繰越。基準日を進めても自動で実績化しない。
- 遅延は売却・元本返済・売却後管理報酬を移動し、元本×年利÷12の追加利息を加算。
- 元本一括返済の簡易モデル。法人税、工事費、減価償却、消費税精算、日割利息は対象外。
- NPVは借入/返済/利息を除く事業CF、ACT/365。表示24か月の外も全期間含める。
- 最低月末残高は月中最低残高ではない。案件フィルター中の残高は選択外CFを除く参考値。
- SQLは原表・公開読取ビュー・実績/未決済予定の月次集計。シナリオ計算はテスト済みPythonで実行。
- 実データを追加すると公開されるため、このデータベースは架空データ専用にする。

[構築手順](docs/setup-plan.md) / [検証状況](docs/verification.md)

公式資料：
- https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
- https://docs.streamlit.io/develop/tutorials/databases/snowflake
