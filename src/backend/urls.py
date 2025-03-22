"""
URL configuration for backend project.

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

from django.contrib import (
    admin,
)
from django.urls import (
    path,
    re_path,
    include,
)

from django.conf import (
    settings,
)
from django.conf.urls.static import (
    static,
)

from django.views.generic.base import (
    RedirectView,
)

from music_app.views import (
    index as musicView,
)

from logging import (
    getLogger,
)

app_name = "backend"
urlpatterns = []

logger = getLogger(app_name)
logger.info(f"Backend is running in DEBUG={settings.DEBUG}")

if settings.DEBUG == True:
    # Force the redirect to the better vite development server (that supports HMR as well)
    logger.warning("Forced redirect to localhost")
    dev_server_url = f"{settings.DJANGO_VITE['default']['dev_server_protocol']}://{settings.DJANGO_VITE['default']['dev_server_host']}:{settings.DJANGO_VITE['default']['dev_server_port']}{settings.DJANGO_VITE['default']['static_url_prefix']}"
    urlpatterns += [
        re_path(
            r"^.*$",
            RedirectView.as_view(
                url=dev_server_url,
                permanent=False,
            ),
            name="index",
        )
    ]
else:
    urlpatterns = [
        path(
            r"admin/",
            admin.site.urls,
            name="admin",
        ),
        path(
            r"music/",
            musicView,
            name="index",
        ),
        # TODO: Add 404 page view and pathing
    ]

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # unnecessary as no Media Root/URL is set in the settings
