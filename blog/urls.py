from django.urls import path
from .views import post_create, post_list, post_detail, post_update

app_name = 'blog'

urlpatterns = [
    path('', post_list),
    path('create/', post_create, name="post_create"),
    path('<int:pk>/update/', post_update),
    path('<int:pk>/', post_detail, name="post_detail")
]