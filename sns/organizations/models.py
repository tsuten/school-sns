import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from shared.abstract_models import AbstractBaseModel

class OrganizationType(models.TextChoices):
    CLASS = "class"
    SCHOOL = "school"
    CIRCLE = "circle"

class EnrollmentManager(models.Manager):
    def get_user_enrollment(self, user_id):
        # 遅延インポートで循環インポートを回避
        from users.models import User
        
        user = User.objects.get(id=user_id)
        classes = Class.objects.filter(students=user)
        schools = [class_obj.school for class_obj in classes if class_obj.school]
        return classes, schools
    
    def get_members(self, class_id):
        class_obj = Class.objects.get(id=class_id)
        return class_obj.students.all()
    
    def get_user_classes(self, user_id):
        from users.models import User
        
        user = User.objects.get(id=user_id)
        classes = Class.objects.filter(students=user)
        return classes
    
    def get_class_info(self, class_id):
        class_obj = Class.objects.get(id=class_id)
        return class_obj
    
    def is_manager(self, user_id, class_id):
        class_obj = Class.objects.get(id=class_id)
        return class_obj.managers.filter(id=user_id).exists()
    
class OrganizationManager(models.Manager):

    def get_organization_type_by_id(self, organization_id):
        """組織タイプを明示的に取得"""
        if Class.objects.filter(id=organization_id).exists():
            return OrganizationType.CLASS
        elif School.objects.filter(id=organization_id).exists():
            return OrganizationType.SCHOOL
        else:
            raise ValidationError("Organization not found")
    
    def get_organization_by_id(self, organization_id, organization_type=None):
        """組織インスタンスを明示的に取得"""
        if organization_type is None:
            organization_type = self.get_organization_type_by_id(organization_id)
        
        if organization_type == OrganizationType.CLASS:
            try:
                return Class.objects.get(id=organization_id)
            except Class.DoesNotExist:
                raise ValidationError(f"Class with id {organization_id} not found")
        elif organization_type == OrganizationType.SCHOOL:
            try:
                return School.objects.get(id=organization_id)
            except School.DoesNotExist:
                raise ValidationError(f"School with id {organization_id} not found")
        else:
            raise ValidationError(f"Unknown organization type: {organization_type}")
        
    def get_user_is_member(self, user_id, organization_id, organization_type=None):
        """メンバーシップチェック（動的処理でfilter実行）"""
        org = self.get_organization_by_id(organization_id, organization_type)
        return org.members.filter(id=user_id).exists()
    
    def get_user_is_manager(self, user_id, organization_id, organization_type=None):
        """マネージャーチェック（動的処理でfilter実行）"""
        org = self.get_organization_by_id(organization_id, organization_type)
        return org.managers.filter(id=user_id).exists()
    
    def get_user_role(self, user_id, organization_id, organization_type=None):
        """ユーザー役割取得（動的処理でAbstractOrganizationメソッド使用）"""
        from users.models import User
        
        org = self.get_organization_by_id(organization_id, organization_type)
        user = User.objects.get(id=user_id)
        return org.get_user_role(user)
    
    def get_organization_members(self, organization_id, organization_type=None):
        """組織メンバー取得（動的処理でAbstractOrganizationメソッド使用）"""
        org = self.get_organization_by_id(organization_id, organization_type)
        org_type = organization_type or self.get_organization_type_by_id(organization_id)
        
        return {
            'members': org.get_members_list(),
            'managers': org.get_managers_list(),
            'members_count': org.get_members_count(),
            'managers_count': org.get_managers_count(),
            'organization_type': org_type,
            'organization_name': org.name
        }
    
    def add_user_to_organization(self, user_id, organization_id, role='member', organization_type=None):
        """ユーザー追加（動的処理でAbstractOrganizationメソッド使用）"""
        from users.models import User
        
        org = self.get_organization_by_id(organization_id, organization_type)
        user = User.objects.get(id=user_id)
        
        if role == 'manager':
            org.add_manager(user)
        elif role == 'member':
            org.add_member(user)
        else:
            raise ValidationError(f"Invalid role: {role}")
        
        return True
    
    def remove_user_from_organization(self, user_id, organization_id, role=None, organization_type=None):
        """ユーザー削除（動的処理でAbstractOrganizationメソッド使用）"""
        from users.models import User
        
        org = self.get_organization_by_id(organization_id, organization_type)
        user = User.objects.get(id=user_id)
        
        if role == 'manager' or role is None:
            if org.is_manager(user):
                org.remove_manager(user)
        
        if role == 'member' or role is None:
            if org.is_member(user):
                org.remove_member(user)
        
        return True
        
class AbstractOrganization(AbstractBaseModel):
    """組織の抽象基底クラス - 統一的なメンバーシップ管理"""
    name = models.CharField(max_length=255, verbose_name="組織名", default="未設定")
    logo = models.ImageField(upload_to='organization_logos/', null=True, blank=True, verbose_name="ロゴ")
    
    # 統一的なメンバーシップ管理
    managers = models.ManyToManyField(
        'users.User', 
        related_name='managed_%(class)ss', 
        blank=True,
        verbose_name="管理者"
    )
    members = models.ManyToManyField(
        'users.User', 
        related_name='%(class)ss_as_member', 
        blank=True,
        verbose_name="メンバー"
    )
    
    class Meta:
        abstract = True
    
    def is_member(self, user):
        """ユーザーがメンバーかチェック（統一API）"""
        return self.members.filter(id=user.id).exists()
    
    def is_manager(self, user):
        """ユーザーが管理者かチェック（統一API）"""
        return self.managers.filter(id=user.id).exists()
    
    def can_send_message(self, user):
        """メッセージ送信権限チェック（統一API）"""
        return self.is_member(user) or self.is_manager(user)
    
    def get_all_users(self):
        """組織の全ユーザーを取得（統一API）"""
        from django.db.models import Q
        from users.models import User
        return User.objects.filter(
            Q(id__in=self.members.all()) | Q(id__in=self.managers.all())
        ).distinct()
    
    def get_members_list(self):
        """メンバー一覧を取得"""
        return self.members.all().order_by('username')
    
    def get_managers_list(self):
        """マネジャー一覧を取得"""
        return self.managers.all().order_by('username')
    
    def get_members_count(self):
        """メンバー数を取得"""
        return self.members.count()
    
    def get_managers_count(self):
        """マネジャー数を取得"""
        return self.managers.count()
    
    def get_user_role(self, user):
        """ユーザーの役割を取得"""
        if self.is_manager(user):
            return "manager"
        elif self.is_member(user):
            return "member"
        else:
            return "none"
    
    def add_member(self, user):
        """メンバーを追加"""
        self.members.add(user)
    
    def remove_member(self, user):
        """メンバーを削除"""
        self.members.remove(user)
    
    def add_manager(self, user):
        """マネジャーを追加"""
        self.managers.add(user)
    
    def remove_manager(self, user):
        """マネジャーを削除"""
        self.managers.remove(user)
    
    def __str__(self):
        return self.name

class Organization(models.Model):
    objects = OrganizationManager()

class School(AbstractOrganization):
    """学校組織モデル"""
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="所在地")
    phone = models.CharField(max_length=255, null=True, blank=True, verbose_name="電話番号")
    email = models.EmailField(max_length=255, null=True, blank=True, verbose_name="メールアドレス")
    website = models.URLField(max_length=255, null=True, blank=True, verbose_name="ウェブサイト")

    objects = EnrollmentManager()
    
    class Meta:
        verbose_name = "学校"
        verbose_name_plural = "学校"

class Class(AbstractOrganization):
    """クラス組織モデル"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, verbose_name="所属学校")
    grade_number = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="学年",
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text="1年から6年まで"
    )
    class_number = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="クラス番号",
        validators=[MinValueValidator(1)],
        help_text="1組以上"
    )
    
    # 後方互換性のためのプロパティ
    @property 
    def students(self):
        """後方互換性：studentsはmembersのエイリアス"""
        return self.members

    objects = EnrollmentManager()

    def get_school_by_class(self, class_id):
        class_obj = Class.objects.get(id=class_id)
        school = class_obj.school
        return school
    
    class Meta:
        verbose_name = "クラス"
        verbose_name_plural = "クラス"