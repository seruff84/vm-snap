# Monitor vmWare vSphere VM Snapshot
I took this code as a basis from this [page](https://vm.knutsson.it/2021/04/get-snapshot-informatin-using-python/)
how to use:
import template 
copy get_vm_snapshot.py to  /usr/lib/zabbix/externalscripts/
in zabbix add macro to host 
{$VCENTER_LOGIN}
{$VCENTER_PASS}
