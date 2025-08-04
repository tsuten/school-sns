from django.db import models


class NotificationType(models.TextChoices):
    # 基本通知
    ANNOUNCEMENT = 'announcement', 'お知らせ'
    MESSAGE = 'message', 'メッセージ'
    
    # 投稿関連
    POST_LIKED = 'post_liked', '投稿にいいね'
    POST_COMMENTED = 'post_commented', '投稿にコメント'
    POST_SHARED = 'post_shared', '投稿がシェア'
    POST_MENTIONED = 'post_mentioned', '投稿で言及'
    POST_REPLIED = 'post_replied', '投稿に返信'
    POST_BOOKMARKED = 'post_bookmarked', '投稿がブックマーク'
    
    # フォロー・関係性関連
    USER_FOLLOWED = 'user_followed', 'フォローされた'
    USER_UNFOLLOWED = 'user_unfollowed', 'フォロー解除'
    FRIEND_REQUEST = 'friend_request', '友達申請'
    FRIEND_ACCEPTED = 'friend_accepted', '友達承認'
    FRIEND_REJECTED = 'friend_rejected', '友達申請拒否'
    
    # チャット・メッセージ関連
    ROOM_INVITED = 'room_invited', 'チャットルームに招待'
    ROOM_JOINED = 'room_joined', 'チャットルームに参加'
    ROOM_LEFT = 'room_left', 'チャットルームから退出'
    ROOM_MESSAGE = 'room_message', 'ルームメッセージ'
    PRIVATE_MESSAGE = 'private_message', 'プライベートメッセージ'
    
    # サークル関連
    CIRCLE_INVITED = 'circle_invited', 'サークルに招待'
    CIRCLE_JOINED = 'circle_joined', 'サークルに参加'
    CIRCLE_LEFT = 'circle_left', 'サークルから退出'
    CIRCLE_ROLE_CHANGED = 'circle_role_changed', 'サークル内役職変更'
    CIRCLE_POST = 'circle_post', 'サークル内投稿'
    CIRCLE_ANNOUNCEMENT = 'circle_announcement', 'サークルお知らせ'
    
    # クラス・組織関連
    CLASS_ANNOUNCEMENT = 'class_announcement', 'クラスお知らせ'
    CLASS_ASSIGNMENT = 'class_assignment', '課題投稿'
    CLASS_SCHEDULE_CHANGED = 'class_schedule_changed', '時間割変更'
    CLASS_JOINED = 'class_joined', 'クラス参加'
    CLASS_LEFT = 'class_left', 'クラス離脱'
    CLASS_ROLE_CHANGED = 'class_role_changed', 'クラス内役職変更'
    
    # イベント関連
    EVENT_INVITED = 'event_invited', 'イベント招待'
    EVENT_REMINDER = 'event_reminder', 'イベントリマインダー'
    EVENT_CANCELLED = 'event_cancelled', 'イベントキャンセル'
    EVENT_UPDATED = 'event_updated', 'イベント更新'
    EVENT_STARTED = 'event_started', 'イベント開始'
    EVENT_ENDED = 'event_ended', 'イベント終了'
    EVENT_JOINED = 'event_joined', 'イベント参加'
    EVENT_LEFT = 'event_left', 'イベント離脱'
    
    # 投票関連
    POLL_CREATED = 'poll_created', '投票作成'
    POLL_VOTED = 'poll_voted', '投票参加'
    POLL_ENDED = 'poll_ended', '投票終了'
    POLL_INVITED = 'poll_invited', '投票に招待'
    POLL_REMINDER = 'poll_reminder', '投票リマインダー'
    
    # カレンダー関連
    SCHEDULE_ADDED = 'schedule_added', 'スケジュール追加'
    SCHEDULE_UPDATED = 'schedule_updated', 'スケジュール更新'
    SCHEDULE_CANCELLED = 'schedule_cancelled', 'スケジュールキャンセル'
    SCHEDULE_REMINDER = 'schedule_reminder', 'スケジュールリマインダー'
    
    # 絵文字・リアクション関連
    EMOJI_REACTION = 'emoji_reaction', '絵文字リアクション'
    CUSTOM_EMOJI_APPROVED = 'custom_emoji_approved', 'カスタム絵文字承認'
    CUSTOM_EMOJI_REJECTED = 'custom_emoji_rejected', 'カスタム絵文字拒否'
    
    # ストレージ・ファイル関連
    FILE_SHARED = 'file_shared', 'ファイル共有'
    FILE_UPLOADED = 'file_uploaded', 'ファイルアップロード'
    FILE_DOWNLOADED = 'file_downloaded', 'ファイルダウンロード'
    STORAGE_QUOTA_WARNING = 'storage_quota_warning', 'ストレージ容量警告'
    
    # システム・アカウント関連
    ACCOUNT_VERIFIED = 'account_verified', 'アカウント認証'
    PASSWORD_CHANGED = 'password_changed', 'パスワード変更'
    LOGIN_ALERT = 'login_alert', 'ログイン通知'
    SECURITY_ALERT = 'security_alert', 'セキュリティ警告'
    PROFILE_UPDATED = 'profile_updated', 'プロフィール更新'
    
    # 学校生活関連
    GRADE_POSTED = 'grade_posted', '成績投稿'
    ATTENDANCE_MARKED = 'attendance_marked', '出席記録'
    ABSENCE_ALERT = 'absence_alert', '欠席アラート'
    HOMEWORK_REMINDER = 'homework_reminder', '宿題リマインダー'
    EXAM_REMINDER = 'exam_reminder', '試験リマインダー'
    
    # ゲーミフィケーション関連
    ACHIEVEMENT_UNLOCKED = 'achievement_unlocked', '実績解除'
    LEVEL_UP = 'level_up', 'レベルアップ'
    BADGE_EARNED = 'badge_earned', 'バッジ獲得'
    MILESTONE_REACHED = 'milestone_reached', 'マイルストーン達成'
    
    # 特別イベント関連
    BIRTHDAY_REMINDER = 'birthday_reminder', '誕生日リマインダー'
    ANNIVERSARY = 'anniversary', '記念日'
    HOLIDAY_NOTICE = 'holiday_notice', '休日のお知らせ'
    WEATHER_ALERT = 'weather_alert', '天気警報'
    
    # システム管理関連
    SYSTEM_NOTICE = 'system_notice', 'システム通知'
    MAINTENANCE = 'maintenance', 'メンテナンス通知'
    UPDATE_AVAILABLE = 'update_available', 'アップデート通知'
    SERVICE_DISRUPTION = 'service_disruption', 'サービス障害'
    
    # 検索・発見関連
    SEARCH_RESULT = 'search_result', '検索結果'
    TRENDING_POST = 'trending_post', 'トレンド投稿'
    RECOMMENDED_USER = 'recommended_user', 'おすすめユーザー'
    RECOMMENDED_CIRCLE = 'recommended_circle', 'おすすめサークル'


# カテゴリ別グループ化
NOTIFICATION_CATEGORIES = {
    '投稿関連': [
        NotificationType.POST_LIKED, 
        NotificationType.POST_COMMENTED, 
        NotificationType.POST_SHARED, 
        NotificationType.POST_MENTIONED, 
        NotificationType.POST_REPLIED, 
        NotificationType.POST_BOOKMARKED
    ],
    'フォロー・関係性': [
        NotificationType.USER_FOLLOWED, 
        NotificationType.USER_UNFOLLOWED, 
        NotificationType.FRIEND_REQUEST, 
        NotificationType.FRIEND_ACCEPTED, 
        NotificationType.FRIEND_REJECTED
    ],
    'チャット・メッセージ': [
        NotificationType.MESSAGE, 
        NotificationType.ROOM_INVITED, 
        NotificationType.ROOM_JOINED, 
        NotificationType.ROOM_LEFT, 
        NotificationType.ROOM_MESSAGE, 
        NotificationType.PRIVATE_MESSAGE
    ],
    'サークル': [
        NotificationType.CIRCLE_INVITED, 
        NotificationType.CIRCLE_JOINED, 
        NotificationType.CIRCLE_LEFT, 
        NotificationType.CIRCLE_ROLE_CHANGED, 
        NotificationType.CIRCLE_POST, 
        NotificationType.CIRCLE_ANNOUNCEMENT
    ],
    'クラス・組織': [
        NotificationType.CLASS_ANNOUNCEMENT, 
        NotificationType.CLASS_ASSIGNMENT, 
        NotificationType.CLASS_SCHEDULE_CHANGED, 
        NotificationType.CLASS_JOINED, 
        NotificationType.CLASS_LEFT, 
        NotificationType.CLASS_ROLE_CHANGED
    ],
    'イベント': [
        NotificationType.EVENT_INVITED, 
        NotificationType.EVENT_REMINDER, 
        NotificationType.EVENT_CANCELLED, 
        NotificationType.EVENT_UPDATED, 
        NotificationType.EVENT_STARTED, 
        NotificationType.EVENT_ENDED, 
        NotificationType.EVENT_JOINED, 
        NotificationType.EVENT_LEFT
    ],
    '投票': [
        NotificationType.POLL_CREATED, 
        NotificationType.POLL_VOTED, 
        NotificationType.POLL_ENDED, 
        NotificationType.POLL_INVITED, 
        NotificationType.POLL_REMINDER
    ],
    'カレンダー': [
        NotificationType.SCHEDULE_ADDED, 
        NotificationType.SCHEDULE_UPDATED, 
        NotificationType.SCHEDULE_CANCELLED, 
        NotificationType.SCHEDULE_REMINDER
    ],
    '学校生活': [
        NotificationType.GRADE_POSTED, 
        NotificationType.ATTENDANCE_MARKED, 
        NotificationType.ABSENCE_ALERT, 
        NotificationType.HOMEWORK_REMINDER, 
        NotificationType.EXAM_REMINDER
    ],
    'システム': [
        NotificationType.ANNOUNCEMENT, 
        NotificationType.SYSTEM_NOTICE, 
        NotificationType.MAINTENANCE, 
        NotificationType.UPDATE_AVAILABLE, 
        NotificationType.SERVICE_DISRUPTION, 
        NotificationType.ACCOUNT_VERIFIED, 
        NotificationType.PASSWORD_CHANGED, 
        NotificationType.LOGIN_ALERT, 
        NotificationType.SECURITY_ALERT
    ],
    'ゲーミフィケーション': [
        NotificationType.ACHIEVEMENT_UNLOCKED, 
        NotificationType.LEVEL_UP, 
        NotificationType.BADGE_EARNED, 
        NotificationType.MILESTONE_REACHED
    ],
    '特別イベント': [
        NotificationType.BIRTHDAY_REMINDER, 
        NotificationType.ANNIVERSARY, 
        NotificationType.HOLIDAY_NOTICE, 
        NotificationType.WEATHER_ALERT
    ],
    'ストレージ・ファイル': [
        NotificationType.FILE_SHARED, 
        NotificationType.FILE_UPLOADED, 
        NotificationType.FILE_DOWNLOADED, 
        NotificationType.STORAGE_QUOTA_WARNING
    ],
    '絵文字・リアクション': [
        NotificationType.EMOJI_REACTION, 
        NotificationType.CUSTOM_EMOJI_APPROVED, 
        NotificationType.CUSTOM_EMOJI_REJECTED
    ],
    '検索・発見': [
        NotificationType.SEARCH_RESULT, 
        NotificationType.TRENDING_POST, 
        NotificationType.RECOMMENDED_USER, 
        NotificationType.RECOMMENDED_CIRCLE
    ]
}