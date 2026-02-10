from django.urls import path
from . import views

urlpatterns = [
    # post_list 这个view对应的URL的名字
    path('', views.post_list, name='post_list' ),
    # post_detail 对应前往详情页的链接，
    # 匹配到'post/<int:pk>/'类型的URL会自动提要转到post_detail View
    # 并且会将这个int类型的参数pk传递到对应的view
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit', views.post_edit, name='post_edit'),
    path('post/<int:pk>/edit-fragment/', views.post_edit_fragment, name='post_edit_fragment'),
    path('post/<int:pk>/cancel-fragment/', views.post_cancel_fragment, name='post_cancel_fragment'),
    path('post/<int:pk>/delete/', views.post_delete, name="post_delete")

]
