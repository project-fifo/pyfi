# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from fifo.helper import *

network_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': '%-10s', 'get': lambda e: d(e, ['name'])},
    'ipranges':
    {'title': 'ipranges', 'len': 36, 'fmt': '%36s', 'get': lambda e: ','.join(d(e, ['ipranges']))},
 }

def create(args):
    res = args.endpoint.create(args.name)
    if res:
        print 'Network successfully created: %s' % res['uuid']
    else:
        print 'Network creation failed: %r' % res
        exit(1)

def add_range(args):
    res = args.endpoint.add_range(args.uuid, args.iprange_uuid)
    if res:
        print 'Successfully added IP range %s to %s' % (args.iprange_uuid, args.uuid)
    else:
        print 'Adding IP range failed: %r' % res
        exit(1)

class Network(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'networks'

    def create(self, name):
        specs = {
            'name': name
        }
        return self._post(specs)

    def add_range(self, network, iprange):
        return self._put_attr(network, 'ipranges/' + iprange, {})

    def make_parser(self, subparsers):
        parser_networks = subparsers.add_parser('networks', help='network related commands')
        parser_networks.set_defaults(endpoint=self)
        subparsers_networks = parser_networks.add_subparsers(help='network commands')
        self.add_metadata_parser(subparsers_networks)
        parser_networks_list = subparsers_networks.add_parser('list', help='lists networks')
        parser_networks_list.add_argument('--fmt', action=ListAction,
                                          default=['uuid', 'name','ipranges'])
        parser_networks_list.add_argument('-H', action='store_false')
        parser_networks_list.add_argument('-p', action='store_true')
        parser_networks_list.set_defaults(func=show_list,
                                          fmt_def=network_fmt)
        parser_networks_get = subparsers_networks.add_parser('get', help='gets a network')
        parser_networks_get.add_argument('uuid')
        parser_networks_get.set_defaults(func=show_get)
        parser_networks_delete = subparsers_networks.add_parser('delete', help='gets a network')
        parser_networks_delete.add_argument('uuid')
        parser_networks_delete.set_defaults(func=show_delete)
        parser_networks_create = subparsers_networks.add_parser('create', help='adds a network')
        parser_networks_create.add_argument('name')
        parser_networks_create.set_defaults(func=create)
        parser_networks_addrange = subparsers_networks.add_parser('add-range', 
                                         help='add an iprange to a network')
        parser_networks_addrange.add_argument('uuid')
        parser_networks_addrange.add_argument('iprange_uuid')
        parser_networks_addrange.set_defaults(func=add_range)
