from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class HostBaseInfo(models.Model):

	hostname = models.CharField(max_length=30,unique=True)
	machine_room = models.CharField(max_length=5)
	create_time = models.DateTimeField('Host Create Time')
    owner = models.CharField(max_length=15)
    account = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    os = models.CharField(max_length=10)
    machine_type = models.CharField(max_length=10)
    remark = models.CharField(max_length=100)

    
    def __unicode__(self):
    	return self.hostname


class HostGroupInfo(models.Model):

    groupname = models.CharField(max_length=30,unique=True)
    remark = models.CharField(max_length=50)

    def __unicode__(self):
    	return self.groupname


class HostMapGroup(models.Model):

	hostbaseinfo = models.ForeignKey(HostBaseInfo)
	groupid = models.IntegerField()

	def __unicode__(self):
		return hostbaseinfo.hostname


class HostIPInfo(models.Model):

	hostbaseinfo = models.ForeignKey(HostBaseInfo)
	ncname = models.CharField(max_length=15)
	ncip = models.IPAddressField()

	def __unicode__(self):
		return hostbaseinfo.hostname

