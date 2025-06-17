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