"""django_forum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'forumapp'
urlpatterns = [
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('settings/<str:channel>/', views.ChannelSettingsView.as_view(), name='channel_settings'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('user/<str:username>/', views.UserView.as_view(), name='user'),
    path('<str:channel>/<int:thread>/', views.CommentView.as_view(), name='comment'),
    path('<str:channel>/', views.ThreadView.as_view(), name='thread'),
    path('', views.ChannelView.as_view(), name='channel'),
]
