from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class MachineRoomInfo(models.Model):

    machine_room = models.CharField(max_length=10,unique=True)

    def __unicode__(self):
        return self.machine_room

class HostEnvCategory(models.Model):

    hostenv = models.CharField(max_length=5,unique=True)

    def __unicode__(self):
        return self.hostenv

class HostBusiSysCate(models.Model):

    business_sys_category = models.CharField(max_length=30,unique=True)

    def __unicode__(self):
        return self.business_sys_category

class AppCategory(models.Model):
    
    app_category = models.CharField(max_length=15,unique=True)

    def __unicode__(self):
        return self.app_category


class HostBaseInfo(models.Model):

    hostname = models.SlugField(max_length=30,unique=True)
    hostenv = models.CharField(max_length=5)
    business_sys_category = models.CharField(max_length=30)
    app_category = models.CharField(max_length=15)
    app_port = models.CharField(max_length=15)

    machine_room = models.CharField(max_length=5)
    phy_machine_flag = models.CharField(max_length=50,blank=True)

    owner = models.CharField(max_length=15)

    os = models.CharField(max_length=10)
    machine_type = models.CharField(max_length=10)

    account = models.CharField(max_length=15,blank=True)
    password = models.CharField(max_length=100,blank=True)

    create_time = models.DateField()
    remark = models.CharField(max_length=100,blank=True)
    

    def __unicode__(self):
        return self.hostname


class HostGroupInfo(models.Model):

    groupname = models.SlugField(max_length=30,unique=True)
    remark = models.CharField(max_length=50,blank=True)

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
    ncip = models.GenericIPAddressField()

    def __unicode__(self):
        return hostbaseinfo.hostname

