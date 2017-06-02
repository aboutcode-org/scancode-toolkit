from django.conf.urls import url
from uploader.handler.views import upload_serializers, upload_form

urlpatterns = [
	url(r'^', upload_serializers, name='upload_serializers'),
]