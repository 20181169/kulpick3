from django.urls import path,re_path, include
from . import views


urlpatterns = [
    path('', views.homepage_views, name='homepage_views'),
    path('<str:slug>-<id>', views.post_views, name='post'),
    path('category/<str:slug>', views.category_views, name="category"),
    path('take_picture/', views.take_picture, name="take_picture"),
    
    
]