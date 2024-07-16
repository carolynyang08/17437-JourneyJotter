"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from socialnetwork import views
from django.contrib.auth import views as auth_views
from django.contrib import admin

urlpatterns = [
    # path('', views.stream_action, name='home'),
    # path('global_stream', views.stream_action, name='global_stream'),
    # path('login', views.login_action, name='login'),
    # path('logout', views.logout_action, name='logout'),
    # path('register', views.register_action, name='register'),
    # path('follower', views.follower_action, name='follower'),
    # path('profile', views.profile_action, name='profile'),
    # path('fake_profile', views.fake_profile_action, name='fake_profile'), 
    
    
    path('', views.stream_action),
    path('socialnetwork/', include('socialnetwork.urls')),
    path('logout', auth_views.logout_then_login, name='logout'),
    path('oauth/', include('social_django.urls', namespace='social')),
    # path('', include('social_django.urls', namespace='social')),

    path('admin/', admin.site.urls), 

    # path("accounts/", include("allauth.urls")),
    # path('admin/', admin.site.urls),
]
