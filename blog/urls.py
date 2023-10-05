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
    path('flowbite_test', views.flowbite_test, name='flowbite_test'),
    #path('upload_done', views.upload_done, name='upload_done'),
    path('ai_recommand', views.ai_recommand, name='ai_recommand'),
    path('ai_recommand_progress', views.ai_recommand_progress, name='ai_recommand_progress'),
    path('menu', views.menu, name="menu"),
    path('picture', views.picture, name="picture"),
    path('menuManage', views.menuManage, name="menuManage"),
    path('special', views.special, name="special"),
    path('speacial_menu', views.speacial_menu, name="speacial_menu"),
    path('speacial_result', views.speacial_result, name="speacial_result"),
    path('upload_speacial_product', views.upload_speacial_product, name="upload_speacial_product"),
    path('time_speacial', views.time_speacial, name="time_speacial"),
]