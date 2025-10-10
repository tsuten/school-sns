from ninja import Schema
import uuid
from apps.core.users.schemas import UserProfileSchema

class ClassInfoSchema(Schema):
    id: uuid.UUID
    name: str
    school: str
    grade_number: int
    class_number: int
    logo: str
    managers: list[UserProfileSchema]
    students: list[UserProfileSchema]
    created_at: str
    updated_at: str

    @classmethod
    def from_class(cls, class_obj):
        """ClassオブジェクトからClassInfoSchemaを作成"""
        return cls(
            id=class_obj.id,
            name=class_obj.name,
            school=class_obj.school.name if class_obj.school else "",
            grade_number=class_obj.grade_number,
            class_number=class_obj.class_number,
            logo=class_obj.logo.url if class_obj.logo else "",
            managers=[UserProfileSchema.from_user(manager) for manager in class_obj.managers.all()],
            students=[UserProfileSchema.from_user(student) for student in class_obj.students.all()],
            created_at=class_obj.created_at.isoformat(),
            updated_at=class_obj.updated_at.isoformat(),
        )