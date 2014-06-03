# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from fifo.helper import *

hypervisor_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 30, 'fmt': '%30s', 'get': lambda e: d(e, ['alias'])},
    'free':
    {'title': 'Free RAM', 'len': 10, 'fmt': '%10s',
     'get': lambda e: str(d(e, ['resources', 'free-memory'])) + 'MB'},
    'used':
    {'title': 'Used RAM', 'len': 10, 'fmt': '%10s',
     'get': lambda e: str(d(e, ['resources', 'provisioned-memory'])) + 'MB'},
    'reserved':
    {'title': 'Reserved RAM', 'len': 10, 'fmt': '%10s',
     'get': lambda e: str(d(e, ['resources', 'reserved-memory'])) + 'MB'},
    'total':
    {'title': 'Total RAM', 'len': 10, 'fmt': '%10s',
     'get': lambda e: str(d(e, ['resources', 'total-memory'])) + 'MB'},
    'smartos':
    {'title': 'SmartOS Version', 'len': 20, 'fmt': '%-20s',
     'get': lambda e: d(e, ['sysinfo', 'Live Image'])},
    'ip':
    {'title': 'IP', 'len': 20, 'fmt': '%20s',
     'get': lambda e: d(e, ['host'])},
}

def map_path(path):
    p =  path.split(":")
    return {"name": p[0], "cost": p[1]}

def set_path(args):
    path = map(map_path, args.path)
    res = args.endpoint.set_path(args.uuid, path)
    if res:
        print "Path set."
    else:
        print "Failed to set path:", res

class Hypervisor(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'hypervisors'
    def set_path(self, uuid, path):
        Arg = {"path": path}
        return self._put_attr(uuid, 'config', Arg)

    def make_parser(self, subparsers):
        parser_hypervisors = subparsers.add_parser('hypervisors', help='hypervisor related commands')
        parser_hypervisors.set_defaults(endpoint=self)
        subparsers_hypervisors = parser_hypervisors.add_subparsers(help='hypervisor commands')
        self.add_metadata_parser(subparsers_hypervisors)
        parser_hypervisors_list = subparsers_hypervisors.add_parser('list', help='lists hypervisors')
        parser_hypervisors_list.add_argument('--fmt', action=ListAction,
                                             default=['uuid', 'name', 'free', 'used', 'reserved'])
        parser_hypervisors_list.add_argument('-H', action='store_false')
        parser_hypervisors_list.add_argument('-p', action='store_true')
        parser_hypervisors_list.set_defaults(func=show_list,
                                          fmt_def=hypervisor_fmt)
        parser_hypervisors_get = subparsers_hypervisors.add_parser('get', help='gets a hypervisor')
        parser_hypervisors_get.add_argument('uuid')
        parser_hypervisors_get.set_defaults(func=show_get)
        parser_hypervisors_delete = subparsers_hypervisors.add_parser('delete', help='deletes a hypervisor')
        parser_hypervisors_delete.add_argument('uuid')
        parser_hypervisors_delete.set_defaults(func=show_delete)

        parser_hypervisors_path = subparsers_hypervisors.add_parser('path', help='sets a hypervisor')
        parser_hypervisors_path.add_argument('uuid')
        parser_hypervisors_path.add_argument('path', nargs='*')
        parser_hypervisors_path.set_defaults(func=set_path)
