# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from fifo.helper import *


grouping_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': '%-10s', 'get': lambda e: d(e, ['name'])},
    'type':
    {'title': 'Name', 'len': 10, 'fmt': '%-10s', 'get': lambda e: d(e, ['type'])},
    'elements':
    {'title': 'elements', 'len': 36, 'fmt': '%36s', 'get': lambda e: ','.join(d(e, ['elements']))},
    'groupings':
    {'title': 'groupings', 'len': 36, 'fmt': '%36s', 'get': lambda e: ','.join(d(e, ['groupings']))},
 }


def create_grouping(args):
    res = args.endpoint.create(args.name, args.type)
    if res:
        print 'New ' + args.type + ' created: ' + res['uuid']
    else:
        print 'Failed to create ' + args.type
        exit(1)

def grouping_add(args):
    main = args.endpoint.get(args.uuid)
    if main['type'] != 'stack':
        print 'Only clusters can be added to stacks.'
        exit(1)
    res = args.endpoint.get(args.target)
    if not res:
        print 'Could not find cluster ' + args.target
        exit(1)
    if not res['type'] == 'cluster':
        print args.target + ' is not a cluster.'
        exit(1)
    res = args.endpoint.add_element(args.uuid, args.target)
    if res:
        print 'Successfully added cluster ' + args.target + '.'
    else:
        print 'Failed to add added cluster ' + args.target + '.'
        exit(1)

def grouping_remove(args):
    main = args.endpoint.get(args.uuid)
    if main['type'] != 'stack':
        print 'Only clusters can be added to stacks.'
        exit(1)
    if main['type'] == 'cluster' and args.type == 'cluster':
        print 'Only VMs can be added to clusters.'
        exit(1)
    res = args.endpoint.delete_element(args.uuid, args.target)
    if res:
        print 'Successfully removed ' + args.type + ' ' + args.target + ' from ' + args.uuid
    else:
        print 'Failed to removed ' + args.type + ' from ' + args.uuid
        exit(1)


class Grouping(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'groupings'

    def create(self, name, type):
        return self._post({'name': name, 'type': type})

    def add_element(self, uuid, element):
        return self._put_attr(uuid, ['elements', element], {})

    def delete_element(self, uuid, element):
        return self._delete_attr(uuid, ['elements', element])

    def make_parser(self, subparsers):
        parser_groupings = subparsers.add_parser('groupings', help='grouping related commands')
        parser_groupings.set_defaults(endpoint=self)
        subparsers_groupings = parser_groupings.add_subparsers(help='grouping commands')
        self.add_metadata_parser(subparsers_groupings)
        parser_groupings_list = subparsers_groupings.add_parser('list', help='lists groupings')
        parser_groupings_list.add_argument('--fmt', action=ListAction,
                                          default=['uuid', 'name', 'type'])
        parser_groupings_list.add_argument('-H', action='store_false')
        parser_groupings_list.add_argument('-p', action='store_true')
        parser_groupings_list.set_defaults(func=show_list,
                                          fmt_def=grouping_fmt)
        parser_groupings_get = subparsers_groupings.add_parser('get', help='gets a grouping')
        parser_groupings_get.add_argument('uuid')
        parser_groupings_get.set_defaults(func=show_get)
        parser_groupings_delete = subparsers_groupings.add_parser('delete', help='deletes a grouping')
        parser_groupings_delete.add_argument('uuid')
        parser_groupings_delete.set_defaults(func=show_delete)

        parser_groupings_create = subparsers_groupings.add_parser('create', help='creates a new grouping')
        parser_groupings_create.add_argument('--type', '-t', required=True, type=str, choices=['stack', 'cluster'])
        parser_groupings_create.add_argument('name')
        parser_groupings_create.set_defaults(func=create_grouping)

        parser_groupings_add = subparsers_groupings.add_parser('add', help='Adds elements to a crouping')
        parser_groupings_add.add_argument('uuid')
        parser_groupings_add.add_argument('type', type=str, choices=['cluster'])
        parser_groupings_add.add_argument('target')
        parser_groupings_add.set_defaults(func=grouping_add)

        parser_groupings_remove = subparsers_groupings.add_parser('remove', help='Removes elements to a crouping')
        parser_groupings_remove.add_argument('uuid')
        parser_groupings_remove.add_argument('type', type=str, choices=['vm', 'cluster'])
        parser_groupings_remove.add_argument('target')
        parser_groupings_remove.set_defaults(func=grouping_remove)
