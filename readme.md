# 目標
- 汎用的で低機能
  - 高機能で非汎用的（カレンダーサービスやチャットサービスみたいに一つの機能に重点を置くものではない）
- 教師と生徒、生徒と生徒が簡単に「交流できる」サービス
  - 交流に重点を置くので先生が生徒を管理する一方向的なサービスではない
  - 教師と生徒を大きく区別するのではなく、権限の管理で区別する
- 外部のチャットサービスなどを必要とせずクラスの連絡や学内の交流もできるようにする
- フォローや友達などの概念よりももっとオープンな繋がりの概念を作る<br>*と言っても一方向と双方向の繋がり以外に何も思いつかないから課題*

# 使用技術
- svelte/sveltekit（javascript）
- python/django
  - django channels
  - django ninja
  - ninjaJWT
  - pillow

# 環境構築
## フロントエンド（sveltekit）
- /web-frontend/appでパッケージを落としてください
  - npm install
- 開発サーバーを起動（ポートはデフォで5173）
  - npm run dev
## バックエンド（django）
- ルートで仮想環境を作成して（venv推奨）モジュールを落としてください（pip推奨）
  - pip install -r requirements
- /snsでモデルをDB（sqlite4）にマイグレート
    - マイグレートに失敗したらDBファイルを削除して個別でモジュールのモデルをマイグレートしてください
    - python manage.py makemigrations {モジュール名}
    - python manage.py migrate
- 終わったらサーバー起動
  - python manage.py runserver
#### ルート
- /api/docs - API仕様書
- /admin - アドミンパネル

# スタイリングルール
#### スタイリングには基本的にtailwindを使用<br>複数箇所で使うことが想定されているものや複雑になるものはCSS
- 角丸めはsmサイズ
- 縁は gray-300
- アイコンはlucideで統一
- CSSは一元的に管理します（web-frontend/app/app.css）
- padidngは4
#### TODO: 文字色を追記

# レスポンススキーマ
{
  "status": "success" / "error",
  "error_code": {str},
  "message": {str}
}
- error_codeにUIの条件分岐で使用するエラーコードを記載
- messageに日本語でわかりやすいエラーの原因を記載