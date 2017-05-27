from __future__ import unicode_literals

from django.db import models

# Create your models here.


class DynamicGroup(models.Model):
	GroupName = models.CharField(max_length=128,unique=True)
	GroupMembers = models.TextField()


class SaltGroup(models.Model):
	GroupName = models.CharField(max_length=128,unique=True)
	GroupExpr = models.TextField()

	