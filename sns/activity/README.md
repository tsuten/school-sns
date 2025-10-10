# Activity Module

ユーザーの行動を一元的に取得できるモジュールです。

## 概要

このモジュールは、SNSアプリケーション内でのユーザーの様々な行動を既存のモジュールから集約し、統一された形式で提供するための機能です。

## 主な機能

- ユーザーの投稿、イベント、投票、サークル参加、メモなどの行動を一元的に取得
- フォローしているユーザーや所属サークルのアクティビティを含むフィード生成
- フィルタリングとページネーション
- アクティビティの統計情報取得

## API エンドポイント

### アクティビティ取得
- `GET /api/activity/user/{user_id}` - 指定ユーザーのアクティビティを取得
- `GET /api/activity/feed` - 認証済みユーザーのフィードアクティビティを取得
- `GET /api/activity/filter` - フィルタリング条件に基づいてアクティビティを取得
- `GET /api/activity/summary/{user_id}` - ユーザーのアクティビティサマリーを取得

## 対応しているアクティビティタイプ

- `post_created` - 投稿作成
- `event_created` - イベント作成
- `poll_created` - 投票作成
- `circle_joined` - サークル参加
- `memo_created` - メモ作成

## 使用方法

### ユーザーのアクティビティを取得

```python
from activity.views import get_user_activities

# 特定ユーザーのアクティビティを取得
activities = get_user_activities(user_id, limit=20, offset=0)
```

### フィード用のアクティビティを取得

```python
from activity.views import get_feed_activities

# フィード用のアクティビティを取得
feed_activities = get_feed_activities(user, limit=50, offset=0)
```

## データ構造

各アクティビティは以下の構造を持ちます：

```json
{
    "id": "アクティビティのID",
    "type": "アクティビティタイプ",
    "description": "アクティビティの説明",
    "user_id": "ユーザーID",
    "username": "ユーザー名",
    "created_at": "作成日時",
    "metadata": {
        "追加情報": "値"
    }
}
```

## 設定

### Django設定への追加

`settings.py`の`INSTALLED_APPS`に追加：

```python
INSTALLED_APPS = [
    # ... 他のアプリ
    'activity',
]
```

### URL設定への追加

メインのURL設定に追加：

```python
from activity.views import router as activity_router

urlpatterns = [
    # ... 他のURL
    path('api/activity/', activity_router.urls),
]
```

## テスト

テストの実行：

```bash
python manage.py test activity
```

## 特徴

- **モデル不要**: 既存のモジュールから情報を集約
- **柔軟性**: 新しいモジュールの追加が容易
- **パフォーマンス**: 必要に応じてデータベースクエリを実行
- **拡張性**: 新しいアクティビティタイプの追加が簡単

## 注意事項

- 各モジュールのモデルが利用できない場合は、そのアクティビティタイプはスキップされます
- 大量のデータがある場合、パフォーマンスに注意が必要です
- フィード生成時は、フォロー数やサークル数に制限を設けています
