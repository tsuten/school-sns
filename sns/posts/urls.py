from ninja import Router
from .models import Post
from .views import api

router = Router()
router.add_router('posts', api, tags=['posts'])