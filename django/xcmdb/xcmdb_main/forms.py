#-*- encoding:utf-8 -*-

from django import forms
from datetime import datetime
from xcmdb_main.models import HostBaseInfo,MachineRoomInfo,HostEnvCategory,HostBusiSysCate,AppCategory


class AddHostForm(forms.ModelForm):

    hostname = forms.SlugField(max_length=30,help_text=u'主机名:')
    hostenv = forms.ModelChoiceField(queryset=HostEnvCategory.objects.all(),help_text=u'所属环境:')
    business_sys_category = forms.ModelChoiceField(queryset=HostBusiSysCate.objects.all(),help_text=u'所属业务:')
    app_category = forms.ModelChoiceField(queryset=AppCategory.objects.all(),help_text=u'应用类型:')
    app_port = forms.CharField(max_length=15,help_text=u'应用端口:')


    machine_room = forms.ModelChoiceField(queryset=MachineRoomInfo.objects.all(),help_text=u'机房:')

    phy_machine_flag = forms.CharField(max_length=50,required=False,help_text=u'机器位置:')

    owner = forms.CharField(max_length=15,help_text=u'拥有者:')
    account = forms.CharField(max_length=15,help_text=u'账号:')
    password = forms.CharField(max_length=100,help_text=u'密码:')

    create_time = forms.DateField(initial=datetime.now().strftime("%Y-%m-%d"),help_text=u'主机创建时间:')
    
    remark = forms.CharField(widget=forms.Textarea,required=False,help_text=u"备注:")

    class Meta:
        model = HostBaseInfo
        exclude = ['os','machine_type',]
    

