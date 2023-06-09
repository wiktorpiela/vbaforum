from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path('verification/', include('verify_email.urls')),
    path("auth/", include("django.contrib.auth.urls")),
    path("chat/", include("chat.urls")),
    path("", include("forumapp.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT)