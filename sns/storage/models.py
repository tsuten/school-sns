import os
import hashlib
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import FileExtensionValidator
from shared.abstract_models import AbstractBaseModel
import uuid
from apps.core.users.models import User
from apps.core.organizations.models import OrganizationType


try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


def get_upload_path(instance, filename):
    """ファイルのアップロードパスを生成"""
    # ファイル名を安全にする
    name, ext = os.path.splitext(filename)
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    
    # カテゴリ別のディレクトリ構造
    if instance.category:
        return f"files/{instance.category.slug}/{safe_filename}"
    return f"files/uncategorized/{safe_filename}"


class FileCategory(AbstractBaseModel):
    """ファイルカテゴリ（プリント、課題、資料など）"""
    name = models.CharField(max_length=100, verbose_name="カテゴリ名")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="スラッグ")
    description = models.TextField(blank=True, verbose_name="説明")
    icon = models.CharField(max_length=50, default="📄", verbose_name="アイコン")
    allowed_extensions = models.JSONField(
        default=list, 
        blank=True,
        help_text="許可するファイル拡張子のリスト（空の場合は全て許可）",
        verbose_name="許可拡張子"
    )
    max_file_size = models.PositiveIntegerField(
        default=10485760,  # 10MB
        help_text="最大ファイルサイズ（バイト）",
        verbose_name="最大ファイルサイズ"
    )
    is_active = models.BooleanField(default=True, verbose_name="有効")

    class Meta:
        verbose_name = "ファイルカテゴリ"
        verbose_name_plural = "ファイルカテゴリ"
        ordering = ['name']

    def __str__(self):
        return f"{self.icon} {self.name}"

    def get_max_size_display(self):
        """ファイルサイズを人間が読みやすい形式で返す"""
        size = self.max_file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    
class StorageItemTag(AbstractBaseModel):
    name = models.CharField(max_length=100, verbose_name="タグ名")

class StorageRoom(AbstractBaseModel):
    name = models.CharField(max_length=100, verbose_name="ルーム名") 
    organization_type = models.CharField(max_length=255, choices=OrganizationType.choices, null=True, blank=True)
    organization_id = models.UUIDField(null=True, blank=True)
    managers = models.ManyToManyField(User, blank=True)

class StorageItem(AbstractBaseModel):
    name = models.CharField(max_length=100, verbose_name="アイテム名")
    file = models.FileField(upload_to='storage/', null=True, blank=True)
    storage_room = models.ForeignKey(StorageRoom, on_delete=models.CASCADE, null=True, blank=True)
    tags = models.ManyToManyField(StorageItemTag, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

class SharedFileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
    def for_user(self, user):
        """ユーザーがアクセス可能なファイルを取得"""
        return self.get_queryset().filter(
            models.Q(uploader=user) |  # 自分がアップロードしたファイル
            models.Q(is_public=True) |  # 公開ファイル
            models.Q(upload_target_type__model='class', upload_target_id__in=user.classes.values_list('id', flat=True))  # 所属クラスのファイル
        ).distinct()


class SharedFile(AbstractBaseModel):
    """共有ファイル"""
    # ファイル情報
    file = models.FileField(
        upload_to=get_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=[
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'txt', 'rtf', 'zip', 'rar', '7z',
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg',
            'mp3', 'mp4', 'avi', 'mov', 'wmv'
        ])],
        verbose_name="ファイル"
    )
    original_name = models.CharField(max_length=255, verbose_name="元のファイル名")
    file_type = models.CharField(max_length=50, blank=True, verbose_name="ファイルタイプ")
    file_size = models.PositiveIntegerField(verbose_name="ファイルサイズ（バイト）")
    checksum = models.CharField(max_length=64, blank=True, verbose_name="チェックサム")
    
    # メタ情報
    title = models.CharField(max_length=200, blank=True, verbose_name="タイトル")
    description = models.TextField(blank=True, verbose_name="説明")
    category = models.ForeignKey(
        FileCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="カテゴリ"
    )
    
    # アップロード情報
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        verbose_name="アップロード者"
    )
    
    # アップロード先（クラス、サークルなど）
    upload_target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="アップロード先タイプ")
    upload_target_id = models.PositiveIntegerField(verbose_name="アップロード先ID")
    upload_target = GenericForeignKey('upload_target_type', 'upload_target_id')
    
    # 公開設定
    is_public = models.BooleanField(default=False, verbose_name="公開ファイル")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    
    objects = SharedFileManager()
    all_objects = models.Manager()  # 削除済みファイルも含む

    class Meta:
        verbose_name = "共有ファイル"
        verbose_name_plural = "共有ファイル"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploader', 'created_at']),
            models.Index(fields=['upload_target_type', 'upload_target_id']),
            models.Index(fields=['category', 'created_at']),
            models.Index(fields=['is_public', 'is_active']),
        ]

    def __str__(self):
        return self.title or self.original_name

    def save(self, *args, **kwargs):
        if self.file and not self.checksum:
            # ファイルのチェックサムを計算
            self.file.seek(0)
            file_hash = hashlib.sha256()
            for chunk in iter(lambda: self.file.read(4096), b""):
                file_hash.update(chunk)
            self.checksum = file_hash.hexdigest()
            self.file.seek(0)
            
            # ファイルサイズを設定
            self.file_size = self.file.size
            
            # ファイルタイプを検出
            if HAS_MAGIC:
                try:
                    self.file.seek(0)
                    file_content = self.file.read(1024)  # 先頭1KBを読む
                    self.file.seek(0)
                    mime = magic.Magic(mime=True)
                    self.file_type = mime.from_buffer(file_content)
                except:
                    self.file_type = 'application/octet-stream'
            else:
                # python-magicが利用できない場合は拡張子から推測
                ext = self.get_extension()
                mime_map = {
                    '.pdf': 'application/pdf',
                    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                    '.png': 'image/png', '.gif': 'image/gif',
                    '.doc': 'application/msword',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    '.txt': 'text/plain',
                }
                self.file_type = mime_map.get(ext, 'application/octet-stream')
            
            # 元のファイル名を保存
            if not self.original_name and hasattr(self.file, 'name'):
                self.original_name = os.path.basename(self.file.name)
        
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """ファイルサイズを人間が読みやすい形式で返す"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def get_extension(self):
        """ファイル拡張子を取得"""
        return os.path.splitext(self.original_name)[1].lower()
    
    def can_access(self, user):
        """ユーザーがこのファイルにアクセス可能かチェック"""
        # アップロード者
        if self.uploader == user:
            return True
        
        # 公開ファイル
        if self.is_public:
            return True
        
        # アップロード先に応じた権限チェック
        from django.contrib.contenttypes.models import ContentType
        
        # クラスにアップロードされたファイル
        class_content_type = ContentType.objects.get(model='class')
        if self.upload_target_type == class_content_type:
            # ユーザーがそのクラスに所属しているかチェック
            return user.classes.filter(id=self.upload_target_id).exists()
        
        # サークルにアップロードされたファイル  
        try:
            circle_content_type = ContentType.objects.get(model='circle')
            if self.upload_target_type == circle_content_type:
                # ユーザーがそのサークルのメンバーかチェック
                from circle.models import Circle
                try:
                    circle = Circle.objects.get(id=self.upload_target_id)
                    return circle.members.filter(id=user.id).exists()
                except Circle.DoesNotExist:
                    return False
        except ContentType.DoesNotExist:
            pass
        
        return False


# ログ履歴機能を一時的に無効化
# class FileAccess(models.Model):
#     """ファイルアクセス履歴"""
#     ACTION_CHOICES = [
#         ('download', 'ダウンロード'),
#         ('view', '閲覧'),
#         ('share', '共有'),
#     ]
#     
#     file = models.ForeignKey(
#         SharedFile, 
#         on_delete=models.CASCADE, 
#         related_name='access_logs',
#         verbose_name="ファイル"
#     )
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE,
#         verbose_name="ユーザー"
#     )
#     action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="アクション")
#     ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IPアドレス")
#     user_agent = models.TextField(blank=True, verbose_name="User Agent")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="実行日時")

#     class Meta:
#         verbose_name = "ファイルアクセス履歴"
#         verbose_name_plural = "ファイルアクセス履歴"
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['file', 'created_at']),
#             models.Index(fields=['user', 'created_at']),
#             models.Index(fields=['action', 'created_at']),
#         ]

#     def __str__(self):
#         return f"{self.user.username} {self.get_action_display()} {self.file.original_name}"