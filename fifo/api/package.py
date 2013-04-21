from .wiggle import Entity
from fifo.helper import *


pkg_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': "%36s", 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': "%-10s", 'get': lambda e: d(e, ['name'])},
    'cpu_cap':
    {'title': 'CPU cap', 'len': 10, 'fmt': "%-10s", 'get': lambda e: str(d(e, ['cpu_cap'])) + "%"},
    'quota':
    {'title': 'Quota', 'len': 10, 'fmt': "%-10s", 'get': lambda e: str(d(e, ['quota'])) + " GB"},
    'ram':
    {'title': 'RAM', 'len': 10, 'fmt': "%-10s", 'get': lambda e: str(d(e, ['ram'])) + " MB"},
}


class Package(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "packages"

    def make_parser(self, subparsers):
        parser_pkgs = subparsers.add_parser('packages', help='package related commands')
        parser_pkgs.set_defaults(endpoint=self)
        subparsers_pkgs = parser_pkgs.add_subparsers(help='package commands')
        parser_pkgs_list = subparsers_pkgs.add_parser('list', help='lists packages')
        parser_pkgs_list.add_argument("--fmt", action=ListAction, default=['uuid', 'name', 'ram', 'cpu_cap', 'quota'])
        parser_pkgs_list.add_argument("-H", action='store_false')
        parser_pkgs_list.add_argument("-p", action='store_true')
        parser_pkgs_list.set_defaults(func=show_list,
                                      fmt_def=pkg_fmt)
        parser_pkgs_get = subparsers_pkgs.add_parser('get', help='gets a package')
        parser_pkgs_get.add_argument("uuid")
        parser_pkgs_get.set_defaults(func=show_get)
        parser_pkgs_delete = subparsers_pkgs.add_parser('delete', help='deletes a package')
        parser_pkgs_delete.add_argument("uuid")
        parser_pkgs_delete.set_defaults(func=show_get)
