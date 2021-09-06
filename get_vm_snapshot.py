#!/bin/env python3
import atexit
import json
from pyVim.connect import SmartConnectNoSSL, Disconnect, vim
from optparse import OptionParser


def get_all_hosts(si: 'pyVmomi.VmomiSupport.vim.ServiceInstance') -> list:
    hosts = []
    content = si.RetrieveContent()
    sub_folders = content.rootFolder.childEntity
    for sf in sub_folders:
        children = sf.hostFolder.childEntity
        for computeresource in children:
            if computeresource.__class__.__name__ == "vim.ClusterComputeResource":
                for host in computeresource.host:
                    if host.summary.runtime.connectionState == 'connected':
                        hosts.append(host)
            elif computeresource.__class__.__name__ == 'vim.Folder':
                for folder in computeresource.childEntity:
                    for host in folder.host:
                        if host.summary.runtime.connectionState == 'connected':
                            hosts.append(host)
            elif computeresource.__class__.__name__ == 'vim.ComputeResource':
                     for host in computeresource.host:
                        if host.summary.runtime.connectionState == 'connected':
                            hosts.append(host)
            else:
                print(f"Skipping: {computeresource.name} as it is not a host")
                continue

    return hosts


def get_all_vm_snapshots(vm):
    results = []
    try:
        rootSnapshots = vm.snapshot.rootSnapshotList
    except:
        rootSnapshots = []

    for snapshot in rootSnapshots:
        results.append(snapshot)
        results += get_child_snapshots(snapshot)

    return results


def get_child_snapshots(snapshot):
    results = []
    snapshots = snapshot.childSnapshotList

    for snapshot in snapshots:
        results.append(snapshot)
        results += get_child_snapshots(snapshot)

    return results


def get_vm_with_snapshot(si):
    hosts = get_all_hosts(si)
    results = []
    for host in hosts:
        vms = host.vm
        for vm in vms:
            if (vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn):
                snapshots = get_all_vm_snapshots(vm)
                if len(snapshots) > 0:
                    results.append(vm)
    return results


def vm_to_json(vms):
    vm_dict = {}
    js_tmpl = '{"data":[]}'
    json_obj = json.loads(js_tmpl)
    for vm in vms:
        vm_dict = {"{#VMNAME}": vm.name}
        json_obj["data"].append(vm_dict)
    return json.dumps(json_obj)



def snapshots_to_json(vms):
    vm_dict = {}
    js_tmpl = '{"vms":{}}'
    json_obj = json.loads(js_tmpl)
    for vm in vms:
        snapshots = get_all_vm_snapshots(vm)
        if len(snapshots) > 0:
            vm_dict = {vm.name: len(snapshots)}
            json_obj["vms"].update(vm_dict)
    return json.dumps(json_obj)



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-v', '--host', dest='hostname',
                      help="vCenter host name")
    parser.add_option('-u', '--user', dest='username',
                      help="vCenter user name")
    parser.add_option('-p', '--password', dest='password',
                      help="vCenter user password")
    parser.add_option('-s', '--snapshots', dest='snapshots',
                      action='store_true', default=False,
                      help="list of vm's snapshot count")

    options, args = parser.parse_args()
    si = SmartConnectNoSSL(host=options.hostname, user=options.username, pwd=options.password, port=443)
    atexit.register(Disconnect, si)
    if options.snapshots:
        result = snapshots_to_json(get_vm_with_snapshot(si))
        print(result)
    else:
        result = vm_to_json(get_vm_with_snapshot(si))
        print(result)
