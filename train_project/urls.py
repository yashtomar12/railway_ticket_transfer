from django.contrib import admin
from django.urls import path, include
from getticket import views   # import views
# ✅ add these imports
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),

    # Root goes to landing page
    path("", views.landing_page, name="landing"),

    # Home (if you want a separate homepage after login)
    path("home/", views.home, name="home"),

    # App URLs
    path("getticket/", include(("getticket.urls", "getticket"), namespace="getticket")),
]

if settings.DEBUG:  # ✅ serve media only in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)