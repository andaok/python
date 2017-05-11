
from django.contrib import admin
from xcmdb_main.models import HostBaseInfo,MachineRoomInfo,AppCategory,HostBusiSysCate,HostEnvCategory


admin.site.register(HostBaseInfo)
admin.site.register(MachineRoomInfo)
admin.site.register(AppCategory)
admin.site.register(HostBusiSysCate)
admin.site.register(HostEnvCategory)

