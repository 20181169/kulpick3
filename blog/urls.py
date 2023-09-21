from django.urls import path,re_path, include
from . import views


urlpatterns = [
    path('', views.homepage_views, name='homepage_views'),
    path('homepage_views_afterLogin', views.homepage_views_afterLogin, name='homepage_views_afterLogin'),
    path('<str:slug>-<id>', views.post_views, name='post'),
    path('category/<str:slug>', views.category_views, name="category"),
    path('take_picture', views.take_picture, name="take_picture"),
    path('upload_product', views.upload_product, name='upload_product'),
    path('login', views.login, name='login'),
    path('wrong_login', views.wrong_login, name='wrong_login'),
    path('select_store', views.select_store, name='select_store'),
    #path('upload_done', views.upload_done, name='upload_done'),
]