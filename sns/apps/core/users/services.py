from django.contrib.auth import get_user_model

User = get_user_model()

def get_user_permission(user_id):
    user = User.objects.get(id=user_id)
    return list(user.get_all_permissions())