from django.conf.urls import include, url


urlpatterns = [
    url(r'^', include('geokey.core.urls')),
]
