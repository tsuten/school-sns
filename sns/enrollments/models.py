import uuid
from django.db import models

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

class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    managers = models.ManyToManyField('users.User', related_name='managed_schools', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EnrollmentManager()
    
    def __str__(self):
        return self.name

class Class(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logo = models.ImageField(upload_to='class_logos/', null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    grade_number = models.IntegerField(null=True, blank=True)
    class_number = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    managers = models.ManyToManyField('users.User', related_name='managed_classes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    students = models.ManyToManyField('users.User', related_name='classes', blank=True)

    objects = EnrollmentManager()

    def get_school_by_class(self, class_id):
        class_obj = Class.objects.get(id=class_id)
        school = class_obj.school
        return school

    def __str__(self):
        return self.name
    
class OrganizationType(models.TextChoices):
    CLASS = "class"
    SCHOOL = "school"
    CIRCLE = "circle"
    PERSONAL = "personal"