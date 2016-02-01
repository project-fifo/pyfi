# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from .package import Package
from .dataset import Dataset
from .org import Org

from fifo.helper import d, header, mk_fmt_str, mk_fmt_line, show_list, show_get
#from fifo.api.package import *
from fifo.api.dataset import ListAction

from datetime import datetime
import sys
import json

import websocket
import thread
import time
import ssl
import tty

def show_services(args):
    e = args.endpoint.get(args.uuid)
    if not e or not e.has_key('services'):
        exit(1)
    services = e['services']
    if args.j:
        print(json.dumps(services, sort_keys=True, indent=2, separators=(',', ': ')))
    else:
        if args.H:
            print('%-20s %s\n' % ('State', 'Service')),
        for service in services.keys():
            state = services[service]
            if args.a or state != 'disabled':
                if args.p:
                    print('%s\t%s' % (state, service))
                else:
                    print('%-20s %s' % (state, service))

def svcadm_action(args):
    if args.endpoint.service_action(args.uuid, args.action, args.service):
        print('Command issued to %s service %s on %s.' % (args.action, args.service, args.uuid))
    else:
        print('Failed to %s service %s on %s.' % (args.action, args.service, args.uuid))
        exit(1)


def vm_action(args):
    if args.action == 'start':
        args.endpoint.start(args.uuid)

    elif args.action == 'stop':
        if args.f:
            args.endpoint.force_stop(args.uuid)
        else:
            args.endpoint.stop(args.uuid)
    elif args.action == 'reboot':
        if args.f:
            args.endpoint.force_reboot(args.uuid)
        else:
            args.endpoint.reboot(args.uuid)

def snapshot_create(args):
    res = args.endpoint.make_snapshot(args.vmuuid, args.comment)
    if res:
        print 'Snapshot successfully created!'
    else:
        print 'Snapshot creation failed!'

def backup_create(args):
    res = args.endpoint.make_backup(args.vmuuid, args.comment, args.d, args.parent)
    if res:
        print 'Snapshot successfully created!'
    else:
        print 'Snapshot creation failed!'

# Helper functions to format the different getters for VM's
def vm_map_fn(vm):
    return(vm['config'])

def vm_raw_map_fn(vm):
    return(vm)

def vm_info_map_fn(vm):
    return(vm['info'])

def vm_metadata_map_fn(vm):
    return(vm['metadata'])

# Returns the ip of a vm (first ip in the networks)
def vm_ip(e):
    n = d(e, ['config', 'networks'], [])
    if len(n) > 0:
        return n[0]['ip']
    else:
        return '-'

vm_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'alias':
    {'title': 'alias', 'len': 10, 'fmt': '%-10s', 'get': lambda e: d(e, ['config', 'alias'])},
    'ip':
    {'title': 'IP', 'len': 15, 'fmt': '%15s', 'get': vm_ip},
    'state':
    {'title': 'state', 'len': 15, 'fmt': '%-15s', 'get': lambda e: d(e, ['state'])},
    'hypervisor':
    {'title': 'hypervisor', 'len': 20, 'fmt': '%-20s', 'get': lambda e: d(e, ['hypervisor'])},
    'package':
    {'title': 'package', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['package'])},
    'dataset':
    {'title': 'dataset', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['config', 'dataset'])},
}

snapshot_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'timestamp':
    {'title': 'Timestamp', 'len': 20, 'fmt': '%-20s',
     'get': lambda e: datetime.fromtimestamp(d(e, ['timestamp'])/1000000).isoformat()},
    'size':
    {'title': 'Size', 'len': 5, 'fmt': '%5d', 'get': lambda e: d(e, ['size'])},
    'comment':
    {'title': 'Comment', 'len': 30, 'fmt': '%-30s', 'get': lambda e: d(e, ['comment'])},
}

backup_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'parent':
    {'title': 'Parent', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['parent'])},
    'local':
    {'title': 'Local', 'len': 5, 'fmt': '%5s', 'get': lambda e: 'Yes' if d(e, ['local']) else 'No'},
    'size':
    {'title': 'Size', 'len': 15, 'fmt': '%5d', 'get': lambda e: d(e, ['size'], 0)},
    'state':
    {'title': 'State', 'len': 10, 'fmt': '%10s', 'get': lambda e: d(e, ['state'])},
    'timestamp':
    {'title': 'Timestamp', 'len': 20, 'fmt': '%-20s',
     'get': lambda e: datetime.fromtimestamp(d(e, ['timestamp'])/1000000).isoformat()},
    'comment':
    {'title': 'Comment', 'len': 30, 'fmt': '%-30s', 'get': lambda e: d(e, ['comment'])},
}

def vm_delete(args):
    if args.l:
        args.endpoint.delete_body(args.uuid, {'location':'hypervisor'})
    else:
        args.endpoint.delete(args.uuid)

def vm_create(args):
    if args.file:
        f = open(args.file, 'r')
        config = json.loads(f.read())
        f.close()
    else:
        config = json.loads(sys.stdin.read())

    wiggle = args.endpoint._wiggle

    package = Package(wiggle).uuid_by_name(args.package)
    if not package:
        print 'Could not find package: ' + args.package + '.'
        exit(1)

    dataset = Dataset(wiggle).uuid_by_name(args.dataset)
    if not dataset:
        print 'Could not find dataset: ' + args.dataset + '.'
        exit(1)

    if args.dryrun:
        reply = args.endpoint.dryrun(package, dataset, config)
    else:
        reply = args.endpoint.create(package, dataset, config)

    if reply == True:
        print 'VM dry run succesful'
    elif reply:
        print 'VM ' + reply['uuid'] + ' created successfully.'
    else:
        print 'Failed to create VM.'

# Shows the data when list was selected.
def snapshots_list(args):
    l = args.endpoint.list_snapshots(args.vmuuid)
    if args.H:
        header(args)
    fmt = mk_fmt_str(args)
    for e in l:
        if not e:
            print('error!')
            exit(1)
        l = mk_fmt_line(args, e)
        if args.p:
            print(':'.join(l))
        else:
            print(fmt%tuple(l))

def backups_list(args):
    l = args.endpoint.list_backups(args.vmuuid)
    l = sorted(l, key=lambda e: d(e, ['timestamp'], 0))
    if args.H:
        header(args)
    fmt = mk_fmt_str(args)
    for e in l:
        if not e:
            print('error!')
            exit(1)
        l = mk_fmt_line(args, e)
        if args.p:
            print(':'.join(l))
        else:
            print(fmt%tuple(l))


def snapshot_get(args):
    e = args.endpoint.get_snapshot(args.vmuuid, args.snapuuid)
    if not e:
        print('error!')
        exit(1)
    if 'map_fn' in args:
        e = args.map_fn(e)
    print(json.dumps(e, sort_keys=True, indent=2, separators=(',', ': ')))

def snapshot_delete(args):
    e = args.endpoint.delete_snapshot(args.vmuuid, args.snapuuid)
    if not e:
        print('error!')
        exit(1)
        print 'Snapshot deleted successfully.'

def snapshot_rollback(args):
    e = args.endpoint.rollback_snapshot(args.vmuuid, args.snapuuid)
    if not e:
        print('error!')
        exit(1)
        print 'Snapshot deleted successfully.'

def backup_get(args):
    e = args.endpoint.get_backup(args.vmuuid, args.snapuuid)
    if not e:
        print('error!')
        exit(1)
    if 'map_fn' in args:
        e = args.map_fn(e)
    print(json.dumps(e, sort_keys=True, indent=2, separators=(',', ': ')))

def backup_verify(args):
    e = args.endpoint.verify_backup(args.vmuuid, args.snapuuid)
    if not e:
        print('error!')
        exit(1)
    ok = True
    fmt = "%-60s %s"
    print fmt % ("File", "State")
    print fmt % (("-" * 60), ('-' * 10))
    for f, hashes in e.iteritems():
        f = f.replace(args.vmuuid, '<vm>')
        if hashes['expected'] == hashes['calculated']:
            print fmt % (f, "OK")
        else:
            print fmt % (f, "ERROR")
    print
    if ok:
        print "Backup OK"
        exit(0)
    else:
        print "Backup corrupted!"
        exit(1)

def backup_delete(args):
    e = args.endpoint.delete_backup(args.vmuuid, args.snapuuid, args.l)
    if not e:
        print('error!')
        exit(1)
        print 'Snapshot deleted successfully.'

def backup_restore(args):
    e = args.endpoint.restore_backup(args.vmuuid, args.snapuuid, args.hypervisor)
    if not e:
        print('error!')
        exit(1)
        print 'Snapshot deleted successfully.'

def ws_msg(ws, msg):
    sys.stdout.write(msg)

def ws_error(ws, error):
    print error
    exit(1)
def ws_close(ws):
    exit(0)

def ws_open(ws):
    def run(*args):
        c = sys.stdin.read(1)
        if not c:
            ws.close()
            exit(0)
        ws.send(c)
        run()
    thread.start_new_thread(run, ())

def console(args):
    w = args.endpoint._wiggle
    r = w.get('sessions', 'one_time_token')
    if not r:
        print "Could not retrive one time token"
        exit(1)
    token = r['token']
    host = w.host
    api = w._apiEndpoint
    endpoint = "wss://" + host + api + "vms/" + args.uuid + "/console?fifo_ott=" + token
    ws = websocket.WebSocketApp(endpoint,
                                on_message = ws_msg,
                                on_error = ws_error,
                                on_close = ws_close)
    ws.on_open = ws_open
    if w.insecure:
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    else:
        ws.run_forever()

def owner_change(args):

    # Validate that we are moving to an existing org
    wiggle = args.endpoint._wiggle
    org = Org(wiggle).uuid_by_name(args.org)
    if not org:
        print 'Could not find org: ' + args.org + ' - cannot complete move!'
        exit(1)

    # make change and validate if successful
    e = args.endpoint.change_owner(args.uuid, args.org)
    if not e:
        print('error!')
        print('Organisation %s not found' % args.org)
        exit(1)
    else:
        update_vm = args.endpoint.get(args.uuid)
        if not update_vm:
            print('error!')
            exit(1)
        elif update_vm['owner'] != args.org:
            print('error!')
            print('MANUAL CHECK - Validation of VM move unsuccessful for ' + args.uuid)
            exit(1)
        else:
            print('VM ownership change successful')
            exit(0)

def run_execute(args):
    r = args.endpoint.execute(args.uuid, args.command, args.args)
    if r:
        print r['output']
        exit(r['exit_code'])
    else:
        print "Failed to execute remote command."
        exit(1)

class VM(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'vms'
        self._fields = ['uuid', 'config', 'state', 'hypervisor', 'package']

    def name_of(self, obj):
        return d(obj, ['config', 'alias'])

    def create(self, package, dataset, config):
        return self._post({'package': package,
                           'dataset': dataset,
                           'config': config})

    def dryrun(self, package, dataset, config):
        return self._wiggle.put(self._resource,'dry_run',
                                 body={'package': package,
                                       'dataset': dataset,
                                       'config': config})

    def start(self, uuid):
        return self._put_attr(uuid, 'state', {'action': 'start'})

    def stop(self, uuid):
        return self._put_attr(uuid, 'state', {'action': 'stop'})

    def reboot(self, uuid):
        return self._put_attr(uuid, 'state', {'action': 'reboot'})

    def execute(self, uuid, cmd, args):
        return self._put_attr(uuid, 'command', {'command': cmd,
                                                'args': args})

    def force_stop(self, uuid):
        return self._put_attr(uuid, 'state', {'action': 'stop', 'force': True})

    def force_reboot(self, uuid):
        return self._put_attr(uuid, 'state', {'action': 'reboot', 'force': True})

    def list_snapshots(self, uuid):
        r = self.get(uuid)
        if r:
            if r['snapshots'] != []:
                # This is fucking ugly!
                map(lambda e: e[1].update({'uuid': e[0]}), r['snapshots'].items())
                return r['snapshots'].values()
            else:
                return []
        else:
            return r

    def make_snapshot(self, uuid, comment):
        return self._post_attr(uuid, 'snapshots', {'comment': comment})

    def service_action(self, uuid, action, service):
        return self._put_attr(uuid, 'services', {'action': action, 'service': service})

    def get_snapshot(self, uuid, snapid):
        r = self.get(uuid)
        if r and r != []:
            return r['snapshots'][snapid]
        else:
            return r

    def delete_snapshot(self, uuid, snapid):
        return self._delete_attr(uuid, 'snapshots/' + snapid)

    def rollback_snapshot(self, uuid, snapid):
        return self._put_attr(uuid, 'snapshots/' + snapid, {'action':'rollback'})

    def list_backups(self, uuid):
        r = self.get(uuid)
        if r:
            if r['backups'] != []:
                # This is fucking ugly!
                map(lambda e: e[1].update({'uuid': e[0]}), r['backups'].items())
                return r['backups'].values()
            else:
                return []
        else:
            return r

    def get_backup(self, uuid, snapid):
        r = self.get(uuid)
        if r:
            return r['backups'][snapid]
        else:
            return r

    def verify_backup(self, uuid, snapid):
        return self._get_attr(uuid, 'backups/' + snapid)

    def delete_backup(self, uuid, snapid, local):
        if local:
            return self._delete_attr_body(uuid, 'backups/' + snapid, {'location':'hypervisor'})
        else:
            return self._delete_attr(uuid, 'backups/' + snapid)

    def restore_backup(self, uuid, snapid, hypervisor):
        if hypervisor:
            Arg = {'action':'rollback', 'hypervisor': hypervisor}
        else:
            Arg = {'action':'rollback'}
        return self._put_attr(uuid, 'backups/' + snapid, Arg)


    def make_backup(self, uuid, comment, delete, parent):
        if parent:
            Arg = {'comment': comment,
                   'delete': delete,
                   'parent': parent}
        else:
            Arg = {'comment': comment,
                   'delete': delete}
        return self._post_attr(uuid, 'backups', Arg)

    def change_owner(self,uuid, org_uuid):
        return self._put_attr(uuid, 'owner', {'org': org_uuid})


    def make_parser(self, subparsers):
        parser_vms = subparsers.add_parser('vms', help='vm related commands')
        parser_vms.set_defaults(endpoint=self)
        subparsers_vms = parser_vms.add_subparsers(help='vm commands')
        self.add_metadata_parser(subparsers_vms)
        parser_vms_list = subparsers_vms.add_parser('list', help='lists a vm')
        parser_vms_list.add_argument('--fmt',
                                     action=ListAction, default=['uuid', 'state', 'alias'],
                                     help='Rows to show, valid options are: uuid, alias, ip, state, hypervisor')
        parser_vms_list.add_argument('-H', action='store_false',
                                     help='Supress the header.')
        parser_vms_list.add_argument('-p', action='store_true',
                                     help='show in parsable format, rows sepperated by colon.')
        parser_vms_list.add_argument('--raw', '-r', action='store_true',
                                    help='print json array of complete data')
        parser_vms_list.set_defaults(func=show_list,
                                     fmt_def=vm_fmt)
        parser_vms_get = subparsers_vms.add_parser('get', help='gets a VM')
        parser_vms_get.add_argument('--raw', '-r', dest='fmt_def', action='store_const',
                                    const=vm_raw_map_fn, default=vm_map_fn,
                                    help='print the raw result not the config version')
        parser_vms_get.add_argument('uuid',
                                    help='uuid of VM to show')
        parser_vms_get.set_defaults(func=show_get)

        parser_vms_execute = subparsers_vms.add_parser('execute', help='executes a VM')
        parser_vms_execute.add_argument('uuid',
                                        help='uuid of VM to show')
        parser_vms_execute.add_argument('command',
                                        help='command to run')
        parser_vms_execute.add_argument('args', metavar='arg', nargs='*',
                                        help='arguments for the command, please make sure to' +
                                        ' escape characters as ";" or ">"')
        parser_vms_execute.set_defaults(func=run_execute)


        parser_vms_svcs = subparsers_vms.add_parser('svcs', help='shows service states on a VM')
        parser_vms_svcs.add_argument('-H', action='store_false',
                                         help='Supress the header.')
        parser_vms_svcs.add_argument('-p', action='store_true',
                                     help='show in parsable format, rows sepperated by tab.')
        parser_vms_svcs.add_argument('-j', action='store_true',
                                     help='show in json.')
        parser_vms_svcs.add_argument('-a', action='store_true',
                                     help='Show disabled services.')
        parser_vms_svcs.add_argument('uuid',
                                     help='uuid of Services on a VM')

        parser_vms_svcs.set_defaults(func=show_services)

        parser_vms_svcadm = subparsers_vms.add_parser('svcadm', help='service administration tasks')
        parser_vms_svcadm.add_argument('uuid',
                                       help='uuid of Services on a VM')

        subparsers_svcadm = parser_vms_svcadm.add_subparsers(help='svcadm commands')

        parser_svcadm_enable = subparsers_svcadm.add_parser('enable', help='enables a service')
        parser_svcadm_enable.set_defaults(action='enable')
        parser_svcadm_enable.set_defaults(func=svcadm_action)
        parser_svcadm_enable.add_argument('service', help='Service to enable')

        parser_svcadm_disable = subparsers_svcadm.add_parser('disable', help='enables a service')
        parser_svcadm_disable.set_defaults(action='disable')
        parser_svcadm_disable.set_defaults(func=svcadm_action)
        parser_svcadm_disable.add_argument('service', help='Service to disable')

        parser_svcadm_clear = subparsers_svcadm.add_parser('clear', help='enables a service')
        parser_svcadm_clear.set_defaults(action='clear')
        parser_svcadm_clear.set_defaults(func=svcadm_action)
        parser_svcadm_clear.add_argument('service', help='Service to en or clear')

        parser_vms_delete = subparsers_vms.add_parser('delete', help='deletes a VM')
        parser_vms_delete.add_argument('-l', action='store_true', default=False,
                                       help='Delete the vm only on the hypervisor.')
        parser_vms_delete.add_argument('uuid',
                                       help='uuid of VM to show')
        parser_vms_delete.set_defaults(func=vm_delete)

        parser_vms_create = subparsers_vms.add_parser('create', help='creates a new VM')
        parser_vms_create.add_argument('--dryrun', action='store_true', default=False,
                                       help='Does not create the machine but simulates if it can be created.')
        parser_vms_create.add_argument('--package', '-p',
                                       help='UUID of the package to use.')
        parser_vms_create.add_argument('--dataset', '-d',
                                       help='UUID of the dataset to use')
        parser_vms_create.add_argument('--file', '-f',
                                       help='Filename of config.json, if not present will be read from STDIN.')
        parser_vms_create.set_defaults(func=vm_create)

        parser_vms_info = subparsers_vms.add_parser('info', help='gets a vm info')
        parser_vms_info.add_argument('uuid',
                                     help='uuid of VM to show')
        parser_vms_info.set_defaults(func=show_get,
                                     map_fn=vm_info_map_fn)

        parser_vms_console = subparsers_vms.add_parser('console', help='consolees to a VM')
        parser_vms_console.add_argument('uuid',
                                     help='uuid of VM to show')
        parser_vms_console.set_defaults(func=console)

        parser_vms_start = subparsers_vms.add_parser('start', help='starts a vm')
        parser_vms_start.add_argument('uuid',
                                      help='uuid of VM to start')
        parser_vms_start.set_defaults(func=vm_action,
                                      action='start')
        parser_vms_stop = subparsers_vms.add_parser('stop', help='stops a vm')
        parser_vms_stop.add_argument('uuid',
                                     help='uuid of VM to stop')
        parser_vms_stop.add_argument('-f', action='store_true')
        parser_vms_stop.set_defaults(func=vm_action,
                                     action='stop')
        parser_vms_reboot = subparsers_vms.add_parser('reboot', help='reboot a vm')
        parser_vms_reboot.add_argument('uuid',
                                       help='uuid of VM to reboot')
        parser_vms_reboot.add_argument('-f', action='store_true')
        parser_vms_reboot.set_defaults(func=vm_action,
                                       action='reboot')
        parser_snapshots = subparsers_vms.add_parser('snapshots', help='snapshot related commands')
        parser_snapshots.add_argument('vmuuid',
                                      help='UUID of the VM to work with.')
        subparsers_snapshots = parser_snapshots.add_subparsers(help='snapshot commands')
        parser_snapshots_list = subparsers_snapshots.add_parser('list', help='lists snapshots')
        parser_snapshots_list.add_argument('--fmt', action=ListAction,
                                           default=['uuid', 'timestamp', 'comment'],
                                           help='Fields to show in the list, valid chances are: uuid, timestamp, comment, hypervisor, dataset and package')
        parser_snapshots_list.add_argument('-H', action='store_false',
                                           help='Supress the header.')
        parser_snapshots_list.add_argument('-p', action='store_true',
                                           help='show in parsable format, rows sepperated by colon.')
        parser_snapshots_list.set_defaults(func=snapshots_list,
                                           fmt_def=snapshot_fmt)
        parser_snapshots_get = subparsers_snapshots.add_parser('get', help='gets snapshots')
        parser_snapshots_get.add_argument('snapuuid',
                                          help='UUID if the snapshot')
        parser_snapshots_get.set_defaults(func=snapshot_get)
        parser_snapshots_delete = subparsers_snapshots.add_parser('delete', help='deletes snapshots')
        parser_snapshots_delete.add_argument('snapuuid',
                                             help='UUID if the snapshot')
        parser_snapshots_delete.set_defaults(func=snapshot_delete)
        parser_snapshots_rollback = subparsers_snapshots.add_parser('rollback', help='rolls back a snapshot')
        parser_snapshots_rollback.add_argument('snapuuid',
                                               help='UUID if the snapshot')
        parser_snapshots_rollback.set_defaults(func=snapshot_rollback)
        parser_snapshots_create = subparsers_snapshots.add_parser('create', help='gets snapshots')
        parser_snapshots_create.add_argument('comment',
                                             help='Comment for the snapshot.')
        parser_snapshots_create.set_defaults(func=snapshot_create)
        parser_backups = subparsers_vms.add_parser('backups', help='backup related commands')
        parser_backups.add_argument('vmuuid',
                                    help='UUID of the VM to work with.')
        subparsers_backups = parser_backups.add_subparsers(help='backup commands')
        parser_backups_list = subparsers_backups.add_parser('list', help='lists backups')
        parser_backups_list.add_argument('--fmt', action=ListAction,
                                         default=['uuid', 'local', 'timestamp', 'comment'],
                                         help='Fields to show in the list, valid chances are: uuid, timestamp, comment')
        parser_backups_list.add_argument('-H', action='store_false',
                                         help='Supress the header.')
        parser_backups_list.add_argument('-p', action='store_true',
                                         help='show in parsable format, rows sepperated by colon.')
        parser_backups_list.set_defaults(func=backups_list,
                                         fmt_def=backup_fmt)

        parser_backups_get = subparsers_backups.add_parser('get', help='gets backups')
        parser_backups_get.add_argument('snapuuid',
                                        help='UUID if the backup')
        parser_backups_get.set_defaults(func=backup_get)

        parser_backups_verify = subparsers_backups.add_parser('verify', help='verifies a backup')
        parser_backups_verify.add_argument('snapuuid',
                                        help='UUID if the backup')
        parser_backups_verify.set_defaults(func=backup_verify)


        parser_backups_delete = subparsers_backups.add_parser('delete', help='deletes backups')
        parser_backups_delete.add_argument('snapuuid',
                                           help='UUID if the backup')
        parser_backups_delete.add_argument('-l', action='store_true', default=False,
                                           help='Delete only local version of the VM.')
        parser_backups_delete.set_defaults(func=backup_delete)
        parser_backups_restore = subparsers_backups.add_parser('restore', help='rolls back a backup')
        parser_backups_restore.add_argument('--hypervisor', default=False,
                                            help='Restore to a specific hypervisor.')
        parser_backups_restore.add_argument('snapuuid',
                                             help='UUID if the backup')
        parser_backups_restore.set_defaults(func=backup_restore)
        parser_backups_create = subparsers_backups.add_parser('create', help='gets backups')
        parser_backups_create.add_argument('--parent', '-p', default=False,
                                           help='The parent of the backup.')
        parser_backups_create.add_argument('comment',
                                           help='Comment for the backup.')
        parser_backups_create.add_argument('-d', action='store_true', default=False,
                                           help='Delete the backup (or parent) after uploading.')
        parser_backups_create.add_argument('--xml', '-x', action='store_true', default=False,
                                           help='Save the VM\'s .xml for restoring.')
        parser_backups_create.set_defaults(func=backup_create)

        parser_vms_owner = subparsers_vms.add_parser('owner', help='changes owner of a vm')
        parser_vms_owner.add_argument('uuid', help='UUID of VM to change owner of')
        parser_vms_owner.add_argument('org', help='UUID of the organisation to move the VM to.')
        parser_vms_owner.set_defaults(func=owner_change)
