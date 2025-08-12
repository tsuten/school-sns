from django.urls import path
from . import views

app_name = 'memo'

urlpatterns = [
    # 従来のDjangoビュー用URL
    path('', views.memo_list_view, name='memo_list'),
    path('create/', views.memo_create_view, name='memo_create'),
    path('<str:memo_id>/', views.memo_detail_view, name='memo_detail'),
    path('<str:memo_id>/update/', views.memo_update_view, name='memo_update'),
    path('<str:memo_id>/delete/', views.memo_delete_view, name='memo_delete'),
]

# Django Ninja Router用のURL（メインのurls.pyでincludeする）
# 例: path('api/memo/', include('apps.memo.urls'))
# そして、メインのurls.pyでrouterを登録する必要があります 