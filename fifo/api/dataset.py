# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import sys
from .wiggle import Entity
from fifo.helper import *
import httplib
import json

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

def _write_bindata(response):
    amt = 4096
    try:
        data = response.read(amt)
    except httplib.IncompleteRead, e:
        data = e.partial
        sys.stdout.write(data)
        sys.stdout.flush()
        return

    while data:
        sys.stdout.write(data)
        sys.stdout.flush()
        try:
            data = response.read(amt)
        except httplib.IncompleteRead, e:
            vprint("Incomplete read captured")
            data = e.partial

def dataset_get(args):
    response = args.endpoint.get_bindata(args.uuid, "/dataset.gz")
    if response:
        vprint("Headers:", response.getheaders())
        _write_bindata(response)

def dataset_put(args):
    try:
        f = open(args.upload, "r")
    except:
        print "Can not open upload file: %s" % args.upload
        exit(1)
    response = args.endpoint._put_file(args.uuid,  "/dataset.gz", f)
    if response:
        if response == 204:
            print "Imported!"
        else:
            print response

def datasets_post(args):
    try:
        f = open(args.upload, "r")
    except:
        print "Can not open upload file: %s" % args.upload
        exit(1)
    response = args.endpoint._post_file(args.uuid, f)
    f.close()
    if response:
        if response == 201:
            print "Created!"
        else:
            print response

class Dataset(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "datasets"

    def name_of(self, obj):
        return obj["name"] + "-" + obj["version"]

    def add_dataset_parser(self, subparsers):
        parser_dataset = subparsers.add_parser('dataset', help='dataset commands')
        parser_dataset.add_argument('uuid', help='uuid of the element to look at')
        subparsers_dataset = parser_dataset.add_subparsers(help='dataset commands')
        parser_dataset_get = subparsers_dataset.add_parser('get', help='Exports the binary dataset')
        parser_dataset_get.set_defaults(func=dataset_get)
        parser_dataset_put = subparsers_dataset.add_parser('put', help='Imports the binary part of a dataset')
        parser_dataset_put.add_argument('--upload', '-u', help="value is file path to be uploaded")
        parser_dataset_put.set_defaults(func=dataset_put)

    def make_parser(self, subparsers):
        parser_datasets = subparsers.add_parser('datasets', help='dataset related commands')
        parser_datasets.set_defaults(endpoint=self)
        subparsers_datasets = parser_datasets.add_subparsers(help='dataset commands')
        self.add_metadata_parser(subparsers_datasets)
        self.add_dataset_parser(subparsers_datasets)
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
        parser_datasets_post = subparsers_datasets.add_parser('post', help='imports a dataset manifest')
        parser_datasets_post.add_argument("uuid")
        parser_datasets_post.add_argument('--upload', '-u', help="the dataset's manifest file to be uploaded")
        parser_datasets_post.set_defaults(func=datasets_post)
