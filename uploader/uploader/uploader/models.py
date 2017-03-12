from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db import models

class Files(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	title = models.CharField(max_length=100, default='default_value')
	docfile = models.FileField(upload_to='file/')
