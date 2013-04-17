from .wiggle import Entity
from fifo.helper import *
from datetime import datetime

def vm_action(args):
    if args.action == 'start':
        args.endpoint.start()
    elif args.action == 'stop':
        if args.f:
            args.endpoint.force_stop()
        else:
            args.endpoint.start()
    elif args.action == 'reboot':
        if args.f:
            args.endpoint.force_reboot()
        else:
            args.endpoint.reboot()


def snapshot_create(args):
    res = args.endpoint.make_snapsot(args.vmuuid, args.comment)
    if res:
        print "Snapshot successfully created!"
    else:
        print "Snapshot creation failed!"

# Helper functions to format the different getters for VM's
def vm_map_fn(vm):
    return(vm['config'])

def vm_info_map_fn(vm):
    return(vm['info'])

def vm_metadata_map_fn(vm):
    return(vm['metadata'])



#Returns the ip of a vm (first ip in the networks)
def vm_ip(e):
    n = d(e, ['config', 'networks'], [])
    if len(n) > 0:
        return n[0]['ip']
    else:
        return "-"


vm_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': "%36s", 'get': lambda e: d(e, ['uuid'])},
    'alias':
    {'title': 'alias', 'len': 10, 'fmt': "%-10s", 'get': lambda e: d(e, ['config', 'alias'])},
    'ip':
    {'title': 'IP', 'len': 15, 'fmt': "%15s", 'get': vm_ip},
    'state':
    {'title': 'state', 'len': 15, 'fmt': "%-15s", 'get': lambda e: d(e, ['state'])},
    'hypervisor':
    {'title': 'hypervisor', 'len': 20, 'fmt': "%-20s", 'get': lambda e: d(e, ['hypervisor'])},
}

snapshot_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': "%36s", 'get': lambda e: d(e, ['uuid'])},
    'timestamp':
    {'title': 'Timestamp', 'len': 20, 'fmt': "%-20s",
     'get': lambda e: datetime.fromtimestamp(d(e, ['timestamp'])/1000000).isoformat()},
    'comment':
    {'title': 'Comment', 'len': 30, 'fmt': "%-30s", 'get': lambda e: d(e, ['comment'])},

}

# Shows the data when list was selected.
def snapshots_list(args):
    l = args.endpoint.list_snapsots(args.vmuuid)
    if args.H:
        header(args)
    fmt = mk_fmt_str(args)
    for e in l:
        if not e:
            print("error!")
            exit(1)
        l = mk_fmt_line(args, e)
        if args.p:
            print(":".join(l))
        else:
            print(fmt%tuple(l))

def snapshot_get(args):
    e = args.endpoint.get_snapsot(args.vmuuid, args.snapuuid)
    if not e:
        print("error!")
        exit(1)
    if 'map_fn' in args:
        e = args.map_fn(e)
    print(json.dumps(e, sort_keys=True, indent=2, separators=(',', ': ')))

def snapshot_delete(args):
    e = args.endpoint.delete_snapsot(args.vmuuid, args.snapuuid)
    if not e:
        print("error!")
        exit(1)
    print "Snapshot deleted successfully."

class VM(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "vms"
    def start(self, uuid):
        return self._put(uuid, {"action": "start"})
    def stop(self, uuid):
        return self._put(uuid, {"action": "start"})
    def reboot(self, uuid):
        return self._put(uuid, {"action": "reboot"})
    def force_stop(self, uuid):
        return self._put(uuid, {"action": "start", "force": True})
    def force_reboot(self, uuid):
        return self._put(uuid, {"action": "reboot", "force": True})
    def list_snapsots(self, uuid):
        return self._wiggle.get_attr(self._resource, uuid, "snapshots")
    def make_snapsot(self, uuid, comment):
        return self._post_attr(uuid, "snapshots", {"comment": comment})
    def get_snapsot(self, uuid, snapid):
        return self._get_attr(uuid, "snapshots/" + snapid)
    def delete_snapsot(self, uuid, snapid):
        return self._delete_attr(uuid, "snapshots/" + snapid)
    def make_parser(self, subparsers):
        parser_vms = subparsers.add_parser('vms', help='vm related commands')
        parser_vms.set_defaults(endpoint=self)
        subparsers_vms = parser_vms.add_subparsers(help='vm commands')
        parser_vms_list = subparsers_vms.add_parser('list', help='lists a vm')
        parser_vms_list.add_argument("--fmt", action=ListAction, default=['uuid', 'hypervisor', 'alias', 'state'])
        parser_vms_list.add_argument("-H", action='store_false')
        parser_vms_list.add_argument("-p", action='store_true')
        parser_vms_list.set_defaults(func=show_list,
                                     fmt_def=vm_fmt)
        parser_vms_get = subparsers_vms.add_parser('get', help='gets a vm')
        parser_vms_get.add_argument("uuid")
        parser_vms_get.set_defaults(func=show_get,
                                    map_fn=vm_map_fn)
        parser_vms_get = subparsers_vms.add_parser('metadata', help='gets a vms metadata')
        parser_vms_get.add_argument("uuid")
        parser_vms_get.set_defaults(func=show_get,
                                    map_fn=vm_metadata_map_fn)
        parser_vms_info = subparsers_vms.add_parser('info', help='gets a vm info')
        parser_vms_info.add_argument("uuid")
        parser_vms_info.set_defaults(func=show_get,
                                     map_fn=vm_info_map_fn)
        parser_vms_start = subparsers_vms.add_parser('start', help='starts a vm')
        parser_vms_start.add_argument("uuid")
        parser_vms_start.set_defaults(func=vm_action,
                                      action='start')
        parser_vms_stop = subparsers_vms.add_parser('stop', help='starts a vm')
        parser_vms_stop.add_argument("uuid")
        parser_vms_stop.add_argument("-f", action='store_true')
        parser_vms_stop.set_defaults(func=vm_action,
                                     action='stop')
        parser_vms_reboot = subparsers_vms.add_parser('reboot', help='starts a vm')
        parser_vms_reboot.add_argument("uuid")
        parser_vms_reboot.add_argument("-f", action='store_true')
        parser_vms_reboot.set_defaults(func=vm_action,
                                       action='reboot')
        parser_snapshots = subparsers_vms.add_parser('snapshots', help='snapshot related commands')
        parser_snapshots.add_argument("vmuuid")
        subparsers_snapshots = parser_snapshots.add_subparsers(help='snapshot commands')
        parser_snapshots_list = subparsers_snapshots.add_parser('list', help='lists snapshots')
        parser_snapshots_list.add_argument("--fmt", action=ListAction,
                                           default=['uuid', 'timestamp', 'comment'])
        parser_snapshots_list.add_argument("-H", action='store_false')
        parser_snapshots_list.add_argument("-p", action='store_true')
        parser_snapshots_list.set_defaults(func=snapshots_list,
                                           fmt_def=snapshot_fmt)
        parser_snapshots_get = subparsers_snapshots.add_parser('get', help='gets snapshots')
        parser_snapshots_get.add_argument("snapuuid")
        parser_snapshots_get.set_defaults(func=snapshot_get)
        parser_snapshots_delete = subparsers_snapshots.add_parser('delete', help='deletes snapshots')
        parser_snapshots_delete.add_argument("snapuuid")
        parser_snapshots_delete.set_defaults(func=snapshot_delete)
        parser_snapshots_create = subparsers_snapshots.add_parser('create', help='gets snapshots')
        parser_snapshots_create.add_argument("comment")
        parser_snapshots_create.set_defaults(func=snapshot_create)

