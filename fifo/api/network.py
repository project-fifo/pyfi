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

class Network(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'networks'

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
