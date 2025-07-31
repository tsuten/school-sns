from django.db import models
from shared.abstract_models import AbstractBaseModel
from users.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class FriendManager(models.Manager):
    def check_friend(self, user1, user2):
        return self.filter(user1=user1, user2=user2).exists() or self.filter(user1=user2, user2=user1).exists()
    
    def get_friends(self, user):
        # user1が自身である場合のuser2のIDリスト
        friends_as_user2 = self.filter(user1=user).values_list('user2__id', flat=True)
        # user2が自身である場合のuser1のIDリスト
        friends_as_user1 = self.filter(user2=user).values_list('user1__id', flat=True)
        # 両方のリストを結合し、重複を排除して返す
        return friends_as_user1.union(friends_as_user2)

class FriendRequestStatus(models.TextChoices):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

class Friend(AbstractBaseModel):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends2')

    objects = FriendManager()

    def clean(self):
        if self.user1 == self.user2:
            raise ValidationError('User cannot be friend with itself')
        if str(self.user1.id) > str(self.user2.id):
            raise ValidationError('User1 must be less than User2')
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user1', 'user2')

class FriendRequestManager(models.Manager):
    def get_pending_friend_requests(self, user):
        # ユーザーがブロックまたは無視しているユーザーのIDを取得
        blocked_users_ids = RelationManagement.objects.get_blocked_users(user)
        ignored_users_ids = RelationManagement.objects.get_ignored_users(user)
        
        # ブロックまたは無視しているユーザーからのリクエストを除外
        return self.filter(to_user=user, status=FriendRequestStatus.PENDING).exclude(
            from_user__id__in=list(blocked_users_ids) + list(ignored_users_ids)
        )

class FriendRequest(AbstractBaseModel):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_from')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_to')
    status = models.CharField(max_length=20, choices=FriendRequestStatus.choices, default=FriendRequestStatus.PENDING)
    status_updated_at = models.DateTimeField(auto_now=True)

    objects = FriendRequestManager()  # カスタムマネージャーを設定

    @staticmethod
    def send_friend_request(from_user, to_user):
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status=FriendRequestStatus.PENDING).exists():
            raise ValidationError('Friend request already exists')
        if Friend.objects.check_friend(from_user, to_user):
            raise ValidationError('Users are already friends')
        FriendRequest.objects.create(from_user=from_user, to_user=to_user, status=FriendRequestStatus.PENDING)
        return FriendRequest.objects.get(from_user=from_user, to_user=to_user)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError('User cannot send friend request to itself')

    def accept(self):
        self.status = FriendRequestStatus.ACCEPTED
        self.status_updated_at = timezone.now()
        self.save()
        # UUIDを文字列として比較し、小さい方をuser1、大きい方をuser2とする
        if str(self.from_user.id) < str(self.to_user.id):
            user1 = self.from_user
            user2 = self.to_user
        else:
            user1 = self.to_user
            user2 = self.from_user
        Friend.objects.create(user1=user1, user2=user2)
        self.delete()

    def reject(self):
        self.status = FriendRequestStatus.REJECTED
        self.status_updated_at = timezone.now()
        self.save()
        self.delete()
        
    class Meta:
        unique_together = ('from_user', 'to_user')

class RelationManagementManager(models.Manager):
    def get_blocked_users(self, user):
        return self.filter(user=user, management=RelationManagementType.BLOCK).values_list('target_user', flat=True)
    
    def get_muted_users(self, user):
        return self.filter(user=user, management=RelationManagementType.MUTE).values_list('target_user', flat=True)
    
    def get_ignored_users(self, user):
        return self.filter(user=user, management=RelationManagementType.IGNORE).values_list('target_user', flat=True)

class RelationManagementType(models.TextChoices):
    BLOCK = 'block'
    MUTE = 'mute'
    IGNORE = 'ignore'

class RelationManagement(AbstractBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relation_management_user')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relation_management_target')
    management = models.CharField(max_length=20, choices=RelationManagementType.choices, default=RelationManagementType.BLOCK)

    objects = RelationManagementManager()

    @staticmethod
    def block_user(user, target_user):
        if RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.BLOCK).exists():
            raise ValidationError('User is already blocked')
        if mute_user := RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.MUTE):
            mute_user.delete()
        if ignore_user := RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.IGNORE):
            ignore_user.delete()
        RelationManagement.objects.create(user=user, target_user=target_user, management=RelationManagementType.BLOCK)
        return RelationManagement.objects.get(user=user, target_user=target_user, management=RelationManagementType.BLOCK)
    
    @staticmethod
    def mute_user(user, target_user): 
        if RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.MUTE).exists():
            raise ValidationError('User is already muted')
        if RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.BLOCK).exists():
            raise ValidationError('User is blocked. You cannot mute a blocked user')
        RelationManagement.objects.create(user=user, target_user=target_user, management=RelationManagementType.MUTE)
        return RelationManagement.objects.get(user=user, target_user=target_user, management=RelationManagementType.MUTE)
    
    @staticmethod
    def ignore_user(user, target_user):   
        if RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.IGNORE).exists():
            raise ValidationError('User is already ignored')
        if RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.BLOCK).exists():
            raise ValidationError('User is blocked. You cannot ignore a blocked user')
        RelationManagement.objects.create(user=user, target_user=target_user, management=RelationManagementType.IGNORE)
        return RelationManagement.objects.get(user=user, target_user=target_user, management=RelationManagementType.IGNORE)
    
    @staticmethod
    def unblock_user(user, target_user):
        if not RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.BLOCK).exists():
            raise ValidationError('User is not blocked')
        RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.BLOCK).delete()
        # 削除後のオブジェクトは存在しないため、成功を示すNoneまたはTrueなどを返す
        return None # または True
    
    @staticmethod
    def unmute_user(user, target_user):
        if not RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.MUTE).exists():
            raise ValidationError('User is not muted')
        RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.MUTE).delete()
        return None # または True
    
    @staticmethod
    def unignore_user(user, target_user):
        if not RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.IGNORE).exists():
            raise ValidationError('User is not ignored')
        RelationManagement.objects.filter(user=user, target_user=target_user, management=RelationManagementType.IGNORE).delete()
        return None # または True

    class Meta:
        unique_together = ('user', 'target_user', 'management')