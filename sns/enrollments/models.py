from django.db import models
from users.models import User

class Class(models.Model):
    grade = models.IntegerField(null=True, blank=True)
    class_ = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    managers = models.ManyToManyField(User, related_name='managed_classes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# class ClassEnrollment(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    class_ = models.ForeignKey(Class, on_delete=models.CASCADE)
#    created_at = models.DateTimeField(auto_now_add=True)
#    updated_at = models.DateTimeField(auto_now=True)
    
#    def __str__(self):
#        return f"{self.user.username} - {self.class.name}"

class School(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

#class SchoolEnrollment(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    created_at = models.DateTimeField(auto_now_add=True)
#    updated_at = models.DateTimeField(auto_now=True)

#    def __str__(self):
#        return f"{self.user.username} - {self.school.name}"