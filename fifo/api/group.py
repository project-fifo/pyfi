from .wiggle import Entity
from fifo.helper import *

group_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': "%36s", 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': "%-10s", 'get': lambda e: d(e, ['name'])},
}

class Group(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "groups"

    def make_parser(self, subparsers):
        parser_groups = subparsers.add_parser('groups', help='group related commands')
        parser_groups.set_defaults(endpoint=self)
        subparsers_groups = parser_groups.add_subparsers(help='group commands')
        parser_groups_list = subparsers_groups.add_parser('list', help='lists groups')
        parser_groups_list.add_argument("--fmt", action=ListAction,
                                          default=['uuid', 'name'])
        parser_groups_list.add_argument("-H", action='store_false')
        parser_groups_list.add_argument("-p", action='store_true')
        parser_groups_list.set_defaults(func=show_list,
                                          fmt_def=group_fmt)
        parser_groups_get = subparsers_groups.add_parser('get', help='gets a group')
        parser_groups_get.add_argument("uuid")
        parser_groups_get.set_defaults(func=show_get)
        parser_groups_delete = subparsers_groups.add_parser('delete', help='gets a group')
        parser_groups_delete.add_argument("uuid")
        parser_groups_delete.set_defaults(func=show_delete)
