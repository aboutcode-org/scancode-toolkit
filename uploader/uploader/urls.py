from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from uploader.views import upload_serializers, upload_form


admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'uploader.views.home', name='home'),
    # url(r'^uploader/', include('uploader.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^admin/', include(admin.site.urls)),
	url(r'^api/', include('uploader.handler.urls')),
]

