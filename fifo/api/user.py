from .wiggle import Entity
from fifo.helper import *


user_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': "%36s", 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': "%-10s", 'get': lambda e: d(e, ['name'])},
    'groups':
    {'title': 'Groups', 'len': 10, 'fmt': "%-10s", 'get': lambda e: str(d(e, ['groups']))},
}


class User(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "users"

    def make_parser(self, subparsers):
        parser_users = subparsers.add_parser('users', help='user related commands')
        parser_users.set_defaults(endpoint=self)
        subparsers_users = parser_users.add_subparsers(help='user commands')
        parser_users_list = subparsers_users.add_parser('list', help='lists users')
        parser_users_list.add_argument("--fmt", action=ListAction,
                                          default=['uuid', 'name'])
        parser_users_list.add_argument("-H", action='store_false')
        parser_users_list.add_argument("-p", action='store_true')
        parser_users_list.set_defaults(func=show_list,
                                          fmt_def=user_fmt)
        parser_users_get = subparsers_users.add_parser('get', help='gets a user')
        parser_users_get.add_argument("uuid")
        parser_users_get.set_defaults(func=show_get)
        parser_users_delete = subparsers_users.add_parser('delete', help='gets a user')
        parser_users_delete.add_argument("uuid")
        parser_users_delete.set_defaults(func=show_delete)
