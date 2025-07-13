from django.shortcuts import render
from ninja import Router
from .models import Class, School
from users.schemas import UserProfileSchema, ClassSchema
from .schemas import ClassInfoSchema
from typing import List
from ninja_jwt.authentication import JWTAuth    

router = Router(tags=["enrollments"])

@router.get("/members/{class_id}", response=List[UserProfileSchema])
def get_members(request, class_id: str):
    members = Class.objects.get_members(class_id)
    return [UserProfileSchema.from_user(member) for member in members]

@router.get("/my_classes", response=List[ClassSchema], auth=JWTAuth())
def get_my_classes(request):
    classes = Class.objects.get_user_classes(request.user.id)
    return [ClassSchema.from_class(class_obj) for class_obj in classes]

@router.get("/class_info/{class_id}", response=ClassInfoSchema, auth=JWTAuth())
def get_class_info(request, class_id: str):
    class_obj = Class.objects.get_class_info(class_id)
    return ClassInfoSchema.from_class(class_obj)