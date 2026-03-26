"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from . import views
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from .admin_views import custom_admin
import django_unicorn


urlpatterns = [

    path('', views.index, name='root'),
    path('asset/<uuid:asset_uuid>/thumb/', views.get_asset_thumbnail, name='get_asset_thumbnail'),
    path('albums/<uuid:album_uuid>/', views.get_album, name='album_detail'),
    path('albums/update', views.update_album, name='update_album'),
    path('search/places', views.search_places, name='search_places'),
    path('api/next-album/', views.next_album, name='next_album'),
    path('api/asset/<uuid:asset_uuid>/update/', views.update_asset, name='update_asset'),
    path('api/pass-album/', views.pass_album, name='pass_album'),
    path('api/reset-queue/', views.reset_queue, name='reset_queue'),

    ####

    path("admin/", admin.site.urls),

    path("", login_required(views.logged_in_home, login_url='/accounts/login/'), name='Profile'),
    path("profile", login_required(views.profile, login_url='/accounts/login/'), name='Profile'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/logout/", views.logout),

    path('register/', views.register, name='register'),
    path('register/submit', views.register_submit, name='register_submit'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path("accounts/logout/", views.logout),
    path("unicorn/", include("django_unicorn.urls")),

    # about the login/logout/register endpoints:
    # https://learndjango.com/tutorials/django-login-and-logout-tutorial
    # https://learndjango.com/tutorials/django-signup-tutorial
    # https://learndjango.com/tutorials/django-best-practices-referencing-user-model

    path('__debug__/', include('debug_toolbar.urls')),
]


admin.autodiscover()