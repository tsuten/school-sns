from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
from organizations.models import OrganizationType
from shared.abstract_models import AbstractBaseModel
from users.models import User
from .utils import check_organization_exists

class EmojiManager(models.Manager):
    def get_by_organization_type(self, org_type):
        """組織タイプで絵文字を取得"""
        return self.get_queryset().filter(organization_type=org_type)
    
    def get_by_organization(self, organization):
        """特定の組織の絵文字を取得"""
        content_type = ContentType.objects.get_for_model(organization)
        return self.get_queryset().filter(
            content_type=content_type,
            object_id=organization.pk
        )
    
    def get_by_circle(self, circle):
        """サークル用絵文字を取得（後方互換性）"""
        from circle.models import Circle
        if isinstance(circle, Circle):
            return self.get_by_organization(circle)
        return self.get_by_organization_type(OrganizationType.CIRCLE)

class Emoji(AbstractBaseModel):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, verbose_name="絵文字名")
    
    # 組織タイプ（参考用、GenericForeignKeyと整合性チェック）
    organization_type = models.CharField(
        max_length=255, 
        choices=OrganizationType.choices, 
        null=True, 
        blank=True,
        verbose_name="組織タイプ"
    )
    
    # GenericForeignKey for type-safe organization reference
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="組織モデル"
    )
    object_id = models.CharField(max_length=36, null=True, blank=True, verbose_name="組織ID")
    organization = GenericForeignKey('content_type', 'object_id')
    
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    image = models.ImageField(upload_to='emojis/', null=True, blank=True, verbose_name="絵文字画像")

    objects = EmojiManager()

    def save(self, *args, **kwargs):
        # organization_typeの自動設定とバリデーション
        if self.organization:
            # GenericForeignKeyから組織タイプを自動推定
            model_name = self.organization._meta.model_name.lower()
            if not check_organization_exists(model_name):
                raise ValueError(f"未対応の組織タイプ: {model_name}")
            
            # 整合性チェック
            if self.organization_type and self.organization_type != model_name:
                raise ValueError(
                    f"組織タイプが一致しません: {self.organization_type} != {model_name}"
                )
            
            self.organization_type = model_name
        
        # スラッグ生成
        org_prefix = self.organization_type or 'general'
        name_slug = self.name.lower().replace(' ', '-')
        self.slug = f"{org_prefix}.{name_slug}"
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """データ整合性バリデーション"""
        from django.core.exceptions import ValidationError
        
        # 組織が設定されている場合の整合性チェック
        if self.organization:
            model_name = self.organization._meta.model_name.lower()
            expected_type = {
                'class': OrganizationType.CLASS,
                'school': OrganizationType.SCHOOL,
                'circle': OrganizationType.CIRCLE,
            }.get(model_name)
            
            if not expected_type:
                raise ValidationError(f"未対応の組織モデル: {model_name}")
            
            if self.organization_type and self.organization_type != expected_type:
                raise ValidationError(
                    f"組織タイプ '{self.organization_type}' と組織モデル '{model_name}' が一致しません"
                )
    
    @property
    def organization_name(self):
        """組織名を取得"""
        return str(self.organization) if self.organization else "なし"

    def __str__(self):
        return self.name