from .models import Post
from ninja import Router
from .schemas import PostSchema, CreatePostSchema
from typing import List
from ninja_jwt.authentication import JWTAuth

router = Router(tags=['posts'])

@router.get('/latest', response=List[PostSchema])
def get_latest_posts(request):
    posts = Post.objects.get_new_posts(count=10)
    return posts

@router.get('/random-within-last-day', response=List[PostSchema])
def get_random_posts(request):
    posts = Post.objects.get_random_within_last_day(count=10)
    return posts

@router.post('', response=PostSchema, auth=JWTAuth())
def create_post(request, post: CreatePostSchema):
    post = Post.objects.post(user=request.auth, title=post.title, content=post.content)
    return post