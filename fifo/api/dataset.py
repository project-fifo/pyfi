# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import sys
from .wiggle import Entity
from fifo.helper import *
import httplib
import json
import argparse

dataset_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': '%-10s', 'get': lambda e: d(e, ['name'])},
    'version':
    {'title': 'Version', 'len': 7, 'fmt': '%-7s', 'get': lambda e: d(e, ['version'])},
    'type':
    {'title': 'Type', 'len': 5, 'fmt': '%-5s', 'get': lambda e: d(e, ['type'])},
    'description':
    {'title': 'Description', 'len': 10, 'fmt': '%-30s', 'get': lambda e: d(e, ['description'])},
}

def _write_bindata(response, f):
    amt = 4096
    try:
        data = response.read(amt)
    except httplib.IncompleteRead, e:
        data = e.partial
        f.write(data)
        f.flush()
        return

    while data:
        f.write(data)
        f.flush()
        try:
            data = response.read(amt)
        except httplib.IncompleteRead, e:
            vprint('Incomplete read captured')
            data = e.partial

def dataset_get(args):
    response = args.endpoint.get_bindata(args.uuid, '/dataset.gz')
    if response:
        vprint('Headers:', response.getheaders())
        _write_bindata(response, args.out or sys.stdout)

def import_dataset(args):
    j = json.load(args.manifest)
    uuid = j['uuid']
    if not args.dataset_only:
        response = args.endpoint._put_attr(uuid, [], j)
        if response:
            print 'Manifest imported'
        else:
            print 'Manifest upload failed.'
            exit(1)

    print 'Uploading dataset now ...'
    response = args.endpoint._put_file([uuid],  '/dataset.gz', args.dataset)
    if response == 204:
        print 'Import complete!'
    else:
        print 'Dataset upload failed.'
        exit(1)

class Dataset(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'datasets'

    def name_of(self, obj):
        return obj['name'] + '-' + obj['version']

    def make_parser(self, subparsers):
        parser_datasets = subparsers.add_parser('datasets', help='dataset related commands')
        parser_datasets.set_defaults(endpoint=self)
        subparsers_datasets = parser_datasets.add_subparsers(help='dataset commands')
        self.add_metadata_parser(subparsers_datasets)
        parser_datasets_list = subparsers_datasets.add_parser('list', help='lists datasets')
        parser_datasets_list.add_argument('--fmt', action=ListAction,
                                          default=['uuid', 'name', 'version', 'type', 'description'])
        parser_datasets_list.add_argument('-H', action='store_false')
        parser_datasets_list.add_argument('-p', action='store_true')
        parser_datasets_list.set_defaults(func=show_list,
                                          fmt_def=dataset_fmt)
        parser_datasets_get = subparsers_datasets.add_parser('get', help='gets a dataset')
        parser_datasets_get.add_argument('uuid')
        parser_datasets_get.set_defaults(func=show_get)
        parser_datasets_delete = subparsers_datasets.add_parser('delete', help='gets a dataset')
        parser_datasets_delete.add_argument('uuid')
        parser_datasets_delete.set_defaults(func=show_delete)
        parser_dataset_import = subparsers_datasets.add_parser('import', help='Imports the binary part of a dataset')
        parser_dataset_import.add_argument('--manifest', '-m', help='manifest to upload',
                                           type=argparse.FileType('r'))
        parser_dataset_import.add_argument('--dataset', '-d', help='dataset to upload',
                                           type=argparse.FileType('r'))
        parser_dataset_import.add_argument('--dataset-only', action='store_true', default=False, help='skip manifest, import dataset only')
        parser_dataset_import.set_defaults(func=import_dataset)
        parser_dataset_export = subparsers_datasets.add_parser('export', help='Exports the dataset binary')
        parser_dataset_export.add_argument('uuid', help='uuid of the element to look at')
        parser_dataset_export.add_argument('--out', '-o', help='File to write to', type=argparse.FileType('w'))
        parser_dataset_export.set_defaults(func=dataset_get)

