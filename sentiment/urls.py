from django.contrib.auth.views import LogoutView
from django.urls import path, include, re_path

from sentiment import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('login/', views.login_function, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    re_path(r'^youtube-update/(?P<id>\d+)/$', views.youtube_update),
    re_path(r'^twitter-update/(?P<id>\d+)/$', views.twitter_update),
    re_path(r'^youtube-result/(?P<id>\d+)/$', views.youtube_result),
    re_path(r'^twitter-result/(?P<id>\d+)/$', views.twitter_result),
    path('add-youtube-link/', views.add_youtube_link, name='add-youtube-link'),
    path('add-twitter-link/', views.add_twitter_link, name='add-twitter-link'),
    path('list-youtube-link/', views.list_youtube_post, name='list-youtube-link'),
    path('list-twitter-link/', views.list_twitter_post, name='list-twitter-link'),
    # path('emp/', views.emp),
    # path('show',views.show),
]
