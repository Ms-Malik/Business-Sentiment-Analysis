from django.urls import path, include

from sentiment import views

urlpatterns = [
    path('login/', views.login_function, name='login'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('index/', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('youtube-result/', views.youtube_result, name='youtube-result'),
    path('twitter-result/', views.twitter_result, name='twitter-result'),
    # path('emp/', views.emp),
    # path('show',views.show),
]
