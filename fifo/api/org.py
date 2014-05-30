# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from fifo.helper import *

org_fmt = {
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
            print 'Org successfully created: %s' % res['uuid']
        else:
            print 'Org creation failed: %r' % res
            exit(1)

class Org(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'orgs'

    def create(self, name):
        return self._post({'name': name})

    def make_parser(self, subparsers):
        parser_orgs = subparsers.add_parser('orgs', help='org related commands')
        parser_orgs.set_defaults(endpoint=self)
        subparsers_orgs = parser_orgs.add_subparsers(help='org commands')
        self.add_metadata_parser(subparsers_orgs)
        parser_orgs_list = subparsers_orgs.add_parser('list', help='lists orgs')
        parser_orgs_list.add_argument('--fmt', action=ListAction,
                                          default=['uuid', 'name'])
        parser_orgs_list.add_argument('-H', action='store_false')
        parser_orgs_list.add_argument('-p', action='store_true')
        parser_orgs_list.set_defaults(func=show_list,
                                          fmt_def=org_fmt)
        parser_orgs_get = subparsers_orgs.add_parser('get', help='gets a org')
        parser_orgs_get.add_argument('uuid')
        parser_orgs_get.set_defaults(func=show_get)
        parser_orgs_delete = subparsers_orgs.add_parser('delete', help='gets a org')
        parser_orgs_delete.add_argument('uuid')
        parser_orgs_delete.set_defaults(func=show_delete)
        parser_orgs_create = subparsers_orgs.add_parser('create', help='creates a Org')
        parser_orgs_create.add_argument('-p', action='store_true')
        parser_orgs_create.add_argument('name')
        parser_orgs_create.set_defaults(func=create)
