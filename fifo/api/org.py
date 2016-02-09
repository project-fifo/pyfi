# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from fifo.helper import *

org_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': '%-10s', 'get': lambda e: d(e, ['name'])},
 }

org_acct_fmt = {
    'resource':
    {'title': 'Resource UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['resource'])},
    'action':
    {'title': 'Action', 'len': 8, 'fmt': '%-8s', 'get': lambda e: d(e, ['action'])},
    'timestamp':
    {'title': 'Timestamp', 'len': 16, 'fmt': '%-16s', 'get': lambda e: d(e, ['timestamp'])},
    'date':
    {'title': 'Timestamp', 'len': 19, 'fmt': '%-19s', 'get': lambda e: t(d(e, ['timestamp']))},
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

def get_accounting(args):
    start_ts = iso_to_ts(args.start)
    end_ts = iso_to_ts(args.end)
    l = args.endpoint.accounting(args.uuid, start_ts, end_ts)
    if args.H:
        header(args)
    fmt = mk_fmt_str(args)
    if args.raw is True:
        print(json.dumps(l, sort_keys=True, indent=2, separators=(',', ': ')))
    else:
        for e in l:
            if not e:
                print('error!')
                exit(1)
            l = mk_fmt_line(args, e)
            if args.p:
                print(':'.join(l))
            else:
                print(fmt%tuple(l))

class Org(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'orgs'

    def create(self, name):
        return self._post({'name': name})

    def accounting(self,uuid, start, end):
        params = "start=%s&end=%s" % (start, end)
        return self._get_attr(uuid, "accounting?%s" % params)

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
        parser_orgs_list.add_argument('--raw', '-r', action='store_true',
                            help='print json array of complete data')
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
        parser_orgs_accounting = subparsers_orgs.add_parser('accounting', help='gets accounting information for an org')
        parser_orgs_accounting.add_argument('--fmt', action=ListAction,
                                            default=['resource', 'action', 'timestamp'],
                                            help='Fields to show in the list, valid chances are: resource, action and timestamp')
        parser_orgs_accounting.add_argument('-H', action='store_false',
                                            help='Supress the header.')
        parser_orgs_accounting.add_argument('-p', action='store_true',
                                            help='show in parsable format, rows sepperated by colon.')
        parser_orgs_accounting.add_argument('--raw', '-r', action='store_true',
                                            help='print json array of complete data')
        parser_orgs_accounting.add_argument('uuid')
        parser_orgs_accounting.add_argument('--start', '-s', help='Timestamp of the start of the accounting period')
        parser_orgs_accounting.add_argument('--end', '-e', help='Timestamp of the end of the accounting period')
        parser_orgs_accounting.set_defaults(func=get_accounting, fmt_def=org_acct_fmt)
