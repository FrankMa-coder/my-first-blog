from django.urls import path
from . import views

urlpatterns = [
    # post_list 这个view对应的URL的名字
    path('', views.post_list, name='post_list' )
]
