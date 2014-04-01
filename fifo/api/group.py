from .wiggle import Entity
from fifo.helper import *

group_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': "%36s", 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': "%-10s", 'get': lambda e: d(e, ['name'])},
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
            print "Group successfully created: %s" % res['uuid']
        else:
            print "Group creation failed: %r" % res
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
            print "Granted %r to %s" % (args.permission, res)
        else:
            print "Grant failed: %r" % res
            exit(1)

class Group(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "groups"

    def create(self, name):
        return self._post({"name": name})

    def grant(self, group, permission):
        return self._put_attr(group, ["permissions"] + permission, {})

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
        parser_groups_create = subparsers_groups.add_parser('create', help='creates a group')
        parser_groups_create.add_argument("-p", action='store_true')
        parser_groups_create.add_argument("name")
        parser_groups_create.set_defaults(func=create)
        parser_groups_grant = subparsers_groups.add_parser('grant', help='grants a permission to a group')
        parser_groups_grant.add_argument("-p", action='store_true')
        parser_groups_grant.add_argument("uuid")
        parser_groups_grant.add_argument("permission", nargs='*')
        parser_groups_grant.set_defaults(func=grant)
