from .wiggle import Entity
from fifo.helper import *


dataset_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': "%36s", 'get': lambda e: d(e, ['dataset'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': "%-10s", 'get': lambda e: d(e, ['name'])},
    'version':
    {'title': 'Version', 'len': 7, 'fmt': "%-7s", 'get': lambda e: d(e, ['version'])},
    'type':
    {'title': 'Type', 'len': 5, 'fmt': "%-5s", 'get': lambda e: d(e, ['type'])},
    'description':
    {'title': 'Description', 'len': 10, 'fmt': "%-30s", 'get': lambda e: d(e, ['description'])},
}


class Dataset(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "datasets"

    def name_of(self, obj):
        return obj["name"] + "-" + obj["version"]

    def make_parser(self, subparsers):
        parser_datasets = subparsers.add_parser('datasets', help='dataset related commands')
        parser_datasets.set_defaults(endpoint=self)
        subparsers_datasets = parser_datasets.add_subparsers(help='dataset commands')
        parser_datasets_list = subparsers_datasets.add_parser('list', help='lists datasets')
        parser_datasets_list.add_argument("--fmt", action=ListAction,
                                          default=['uuid', 'name', 'version', 'type', 'description'])
        parser_datasets_list.add_argument("-H", action='store_false')
        parser_datasets_list.add_argument("-p", action='store_true')
        parser_datasets_list.set_defaults(func=show_list,
                                          fmt_def=dataset_fmt)
        parser_datasets_get = subparsers_datasets.add_parser('get', help='gets a dataset')
        parser_datasets_get.add_argument("uuid")
        parser_datasets_get.set_defaults(func=show_get)
        parser_datasets_delete = subparsers_datasets.add_parser('delete', help='gets a dataset')
        parser_datasets_delete.add_argument("uuid")
        parser_datasets_delete.set_defaults(func=show_delete)
