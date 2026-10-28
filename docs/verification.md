# 検証状況

2026-10-29 日本時間

## ローカル実行済み

- Python 3.12.14。requirements.txtの4依存パッケージを隔離venvにインストール済み。
- `python -m unittest discover -s tests -v`: **17テスト成功**（計算12、Streamlit AppTest 4、接続初期化1）。
- 正常系：3案件54明細、初月末90,000,000円、24か月末201,550,000円。
- 3か月遅延：売却/元本返済/管理報酬移動、利息1,725,000円増、24か月末199,825,000円。
- UI：標準→遅延→標準復帰、案件選択解除→再選択、カスタム条件、エラー時停止。
- 実績置換、元データ非破壊、未決済繰越、うるう年、NPV借入除外、未来/不完全/重複実績の検知。
- Pythonコンパイル検査成功。

AppTestは実ブラウザのスクリーンショット検証や公開URL確認の代わりではありません。

## Snowflake実環境

- 所有者のGoogle認証でSnowsightログイン成功（親担当による確認）。
- CF_DEMO.RAW/MART、PROJECTS/CASH_EVENTSの作成を確認。
- 初期投入には既存XS Warehouseを使用。その後、公開アプリ専用 `CF_DEMO_WH` を設定。
- シードMERGE実行成功、CASH_EVENTSが54件と実測確認（親担当）。
- 公開ビュー作成済み。PUBLIC_PROJECTS 3件、PUBLIC_CASH_EVENTS 54件を確認（親担当）。
- 専用ユーザー `CF_DEMO_APP`、ロール `CF_DEMO_READER`、鍵ペアで外部Python接続成功。
- 固定SELECTで公開ビュー3案件/54明細を取得。現在のユーザー/ロール/WHを照合済み。
- SHOW GRANTSでDB USAGE、MART USAGE、2公開VIEW SELECT、専用WH USAGEの5権限を確認。
- 最初の接続はSDKが不要なクラウドメタデータ探索を試みたため拒否。公式オプション `SNOWFLAKE_DISABLE_PLATFORM_DETECTION=true` をプロセス開始前に設定して探索を除去し、同じ接続先で正常成功。アプリにも初期化前の設定を固定。
- 接続はclose済み。Snowflake実接続の成功と、公開ホストからのE2Eは別に扱う。

## 公開

- 外部ホストへの登録/リポジトリ連携/専用読取ユーザーと鍵保存はユーザー承認取得済み。設定作業は親担当が実施。
- 公開URLなし。匿名アクセスのE2Eは未実施。
- リポジトリは非公開、Secretsをソースに保存していません。
