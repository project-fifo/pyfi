# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from fifo.helper import *


dtrace_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 40, 'fmt': '%-40s', 'get': lambda e: d(e, ['name'])},
}


class Dtrace(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'dtrace'

    def make_parser(self, subparsers):
        parser_dtraces = subparsers.add_parser('dtrace', help='dtrace related commands')
        parser_dtraces.set_defaults(endpoint=self)
        subparsers_dtraces = parser_dtraces.add_subparsers(help='dtrace commands')
        self.add_metadata_parser(subparsers_dtraces)
        parser_dtraces_list = subparsers_dtraces.add_parser('list', help='lists dtraces')
        parser_dtraces_list.add_argument('--fmt', action=ListAction,
                                          default=['uuid', 'name'])
        parser_dtraces_list.add_argument('-H', action='store_false')
        parser_dtraces_list.add_argument('-p', action='store_true')
        parser_dtraces_list.set_defaults(func=show_list,
                                          fmt_def=dtrace_fmt)
        parser_dtraces_get = subparsers_dtraces.add_parser('get', help='gets a dtrace')
        parser_dtraces_get.add_argument('uuid')
        parser_dtraces_get.set_defaults(func=show_get)
        parser_dtraces_delete = subparsers_dtraces.add_parser('delete', help='gets a dtrace')
        parser_dtraces_delete.add_argument('uuid')
        parser_dtraces_delete.set_defaults(func=show_delete)
