from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Circle, CircleMessage, CircleNotification


@receiver(post_save, sender=Circle)
def add_founder_to_members(sender, instance, created, **kwargs):
    """サークル作成時に創始者をメンバーに自動追加"""
    if created and instance.founder:
        instance.members.add(instance.founder)


@receiver(m2m_changed, sender=Circle.members.through)
def check_banned_users_on_member_add(sender, instance, action, pk_set, **kwargs):
    """メンバー追加時にBANユーザーチェック"""
    if action == 'pre_add' and pk_set:
        banned_user_ids = set(instance.banned_users.values_list('id', flat=True))
        banned_users_to_add = pk_set.intersection(banned_user_ids)
        if banned_users_to_add:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            banned_usernames = list(User.objects.filter(id__in=banned_users_to_add).values_list('username', flat=True))
            raise ValidationError(f"BANされたユーザーをメンバーに追加することはできません: {', '.join(banned_usernames)}")


@receiver(m2m_changed, sender=Circle.moderators.through)
def check_banned_users_on_moderator_add(sender, instance, action, pk_set, **kwargs):
    """モデレーター追加時にBANユーザーチェック"""
    if action == 'pre_add' and pk_set:
        banned_user_ids = set(instance.banned_users.values_list('id', flat=True))
        banned_users_to_add = pk_set.intersection(banned_user_ids)
        if banned_users_to_add:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            banned_usernames = list(User.objects.filter(id__in=banned_users_to_add).values_list('username', flat=True))
            raise ValidationError(f"BANされたユーザーをモデレーターに追加することはできません: {', '.join(banned_usernames)}")
    elif action == 'post_add' and pk_set:
        # モデレーターに追加されたユーザーを自動的にメンバーにも追加
        instance.members.add(*pk_set)


@receiver(m2m_changed, sender=Circle.banned_users.through)
def handle_banned_users_change(sender, instance, action, pk_set, **kwargs):
    """BANユーザーが変更された時の処理"""
    if action == 'post_add':
        # BANされたユーザーをメンバーとモデレーターから削除
        if pk_set:
            instance.members.remove(*pk_set)
            instance.moderators.remove(*pk_set)
            print(f"ユーザー {pk_set} をサークル '{instance.name}' からBANしました（メンバー・モデレーター権限も削除）")
    elif action == 'post_remove':
        print(f"ユーザー {pk_set} のBAN解除がサークル '{instance.name}' で実行されました")


@receiver(m2m_changed, sender=Circle.members.through)
def send_member_notification_to_circle(sender, instance, action, pk_set, **kwargs):
    """メンバーが変更された時にサークルのメンバーに通知を送信"""
    if action == 'post_add' and pk_set:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(id__in=pk_set)
        for user in users:
            CircleNotification.objects.create(
                circle=instance,
                message=f"ユーザー {user.username} が参加しました"
            )
    elif action == 'post_remove' and pk_set:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(id__in=pk_set)
        for user in users:
            CircleNotification.objects.create(
                circle=instance,
                message=f"ユーザー {user.username} が退出しました"
            )

# channels
@receiver(post_save, sender=CircleMessage)
def send_message_to_circle(sender, instance, created, **kwargs):
    """メッセージが作成された時にサークルのメンバーにWebSocket経由で送信"""
    if created:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        circle_group_name = f'circle_chat_{instance.circle.id}'
        
        # WebSocketグループにメッセージを送信
        async_to_sync(channel_layer.group_send)(
            circle_group_name,
            {
                'type': 'chat_message',
                'message_id': str(instance.id),
                'message': instance.content,
                'user_id': str(instance.user.id),
                'username': instance.user.username,
                'timestamp': instance.created_at.isoformat(),
            }
        )
        
        print(f"メッセージをWebSocketで送信しました: {instance.content}")