# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from fifo.helper import *

role_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': '%-10s', 'get': lambda e: d(e, ['name'])},
}

def create(args):
    res = args.endpoint.create(args.name)
    if args.p:
        if res:
            print res['uuid']
        else:
            exit(1)
    else:
        if res:
            print 'Role successfully created: %s' % res['uuid']
        else:
            print 'Role creation failed: %r' % res
            exit(1)

def grant(args):
    res = args.endpoint.grant(args.uuid, args.permission)
    if args.p:
        if res:
            exit(0)
        else:
            exit(1)
    else:
        if res:
            print 'Granted %r to %s' % (args.permission, res)
        else:
            print 'Grant failed: %r' % res
            exit(1)

class Role(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'roles'

    def create(self, name):
        return self._post({'name': name})

    def grant(self, role, permission):
        return self._put_attr(role, ['permissions'] + permission, {})

    def make_parser(self, subparsers):
        parser_roles = subparsers.add_parser('roles', help='role related commands')
        parser_roles.set_defaults(endpoint=self)
        subparsers_roles = parser_roles.add_subparsers(help='role commands')
        self.add_metadata_parser(subparsers_roles)
        parser_roles_list = subparsers_roles.add_parser('list', help='lists roles')
        parser_roles_list.add_argument('--fmt', action=ListAction,
                                          default=['uuid', 'name'])
        parser_roles_list.add_argument('-H', action='store_false')
        parser_roles_list.add_argument('-p', action='store_true')
        parser_roles_list.set_defaults(func=show_list,
                                          fmt_def=role_fmt)
        parser_roles_get = subparsers_roles.add_parser('get', help='gets a role')
        parser_roles_get.add_argument('uuid')
        parser_roles_get.set_defaults(func=show_get)
        parser_roles_delete = subparsers_roles.add_parser('delete', help='gets a role')
        parser_roles_delete.add_argument('uuid')
        parser_roles_delete.set_defaults(func=show_delete)
        parser_roles_create = subparsers_roles.add_parser('create', help='creates a role')
        parser_roles_create.add_argument('-p', action='store_true')
        parser_roles_create.add_argument('name')
        parser_roles_create.set_defaults(func=create)
        parser_roles_grant = subparsers_roles.add_parser('grant', help='grants a permission to a role')
        parser_roles_grant.add_argument('-p', action='store_true')
        parser_roles_grant.add_argument('uuid')
        parser_roles_grant.add_argument('permission', nargs='*')
        parser_roles_grant.set_defaults(func=grant)
