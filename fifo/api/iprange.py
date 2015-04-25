# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from fifo.helper import *

iprange_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 20, 'fmt': '%-20s', 'get': lambda e: d(e, ['name'])},
    'tag':
    {'title': 'Tag', 'len': 10, 'fmt': '%-10s', 'get': lambda e: d(e, ['tag'])},
    'iprange':
    {'title': 'Iprange', 'len': 15, 'fmt': '%15s', 'get': lambda e: d(e, ['iprange'])},
    'first':
    {'title': 'First', 'len': 15, 'fmt': '%15s', 'get': lambda e: d(e, ['first'])},
    'next':
    {'title': 'Next', 'len': 15, 'fmt': '%15s', 'get': lambda e: d(e, ['current'])},
    'last':
    {'title': 'Last', 'len': 15, 'fmt': '%15s', 'get': lambda e: d(e, ['last'])},
    'returned':
    {'title': 'Returned', 'len': 15, 'fmt': '%15s', 'get': lambda e: len(d(e, ['free'], []))},
    'gateway':
    {'title': 'Gateway', 'len': 15, 'fmt': '%15s', 'get': lambda e: d(e, ['gateway'])},
    'netmask':
    {'title': 'Netmask', 'len': 15, 'fmt': '%15s', 'get': lambda e: d(e, ['netmask'])},
    'vlan':
    {'title': 'vlan', 'len': 5, 'fmt': '%5s', 'get': lambda e: d(e, ['vlan'])},
}

def create(args):

    if args.vlan:
        res = args.endpoint.create(args.name, args.network, args.netmask, args.gateway,
                                args.first, args.last, args.tag, int(args.vlan))
    else:
        res = args.endpoint.create(args.name, args.network, args.netmask, args.gateway, 
                                args.first, args.last, args.tag)
    if res:
        print 'IP range successfully created: %s' % res['uuid']
    else:
        print 'IP range creation failed: %r' % res
        exit(1)

class Iprange(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'ipranges'

    def create(self, name, network, netmask, gateway, first, last, nic_tag, vlan=None):
        specs = {
            'name': name,
            'network': network,
            'netmask': netmask,
            'gateway': gateway,
            'first': first,
            'last': last,
            'tag': nic_tag,
        }
        if vlan > 0:
            specs['vlan'] = vlan

        return self._post(specs)

    def make_parser(self, subparsers):
        parser_ipranges = subparsers.add_parser('ipranges', help='iprange related commands')
        parser_ipranges.set_defaults(endpoint=self)
        subparsers_ipranges = parser_ipranges.add_subparsers(help='iprange commands')
        self.add_metadata_parser(subparsers_ipranges)
        parser_ipranges_list = subparsers_ipranges.add_parser('list', help='lists ipranges')
        parser_ipranges_list.add_argument('--fmt', action=ListAction,
                                          default=['uuid', 'name', 'tag', 'first', 'last', 'vlan'])
        parser_ipranges_list.add_argument('-H', action='store_false')
        parser_ipranges_list.add_argument('-p', action='store_true')
        parser_ipranges_list.set_defaults(func=show_list,
                                          fmt_def=iprange_fmt)
        parser_ipranges_get = subparsers_ipranges.add_parser('get', help='gets an iprange')
        parser_ipranges_get.add_argument('uuid')
        parser_ipranges_get.set_defaults(func=show_get)
        parser_ipranges_delete = subparsers_ipranges.add_parser('delete', help='deletes an iprange')
        parser_ipranges_delete.add_argument('uuid')
        parser_ipranges_delete.set_defaults(func=show_delete)
        parser_ipranges_create = subparsers_ipranges.add_parser('create', help='creates an ip range')
        parser_ipranges_create.add_argument('name')
        parser_ipranges_create.add_argument('--network', '-n', required=True, help='Network for the iprange.')
        parser_ipranges_create.add_argument('--netmask', '-m', required=True, help='Netmask for the iprange.')
        parser_ipranges_create.add_argument('--gateway', '-g', required=True, help='Gateway for the iprange.')
        parser_ipranges_create.add_argument('--first', '-f', required=True, help='First assignable IP address for the iprange.')
        parser_ipranges_create.add_argument('--last', '-l', required=True, help='Last assignable IP address for the iprange.')
        parser_ipranges_create.add_argument('--tag', '-t', required=True,
                                help='NIC Tag to use for the iprange. This must exist on at least one hypervisor')
        parser_ipranges_create.add_argument('--vlan', '-v', type=int, help='Vlan for the iprange.')
        parser_ipranges_create.set_defaults(func=create)
