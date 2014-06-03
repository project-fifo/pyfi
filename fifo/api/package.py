# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from fifo.helper import *
import re

pkg_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': '%-10s', 'get': lambda e: d(e, ['name'])},
    'cpu_cap':
    {'title': 'CPU cap', 'len': 10, 'fmt': '%-10s', 'get': lambda e: str(d(e, ['cpu_cap'])) + '%'},
    'quota':
    {'title': 'Quota', 'len': 10, 'fmt': '%-10s', 'get': lambda e: str(d(e, ['quota'])) + ' GB'},
    'ram':
    {'title': 'RAM', 'len': 10, 'fmt': '%-10s', 'get': lambda e: str(d(e, ['ram'])) + ' MB'},
}


def create(args):
    mb = 1024*1024
    gb = mb * 1024
    reqs = []
    if args.requirement:
        reqs = map(package_rule, args.requirement)
    if args.random:
        reqs += map(package_random, args.random)
    if args.scale:
        reqs += map(package_scale, args.scale)
    if args.memory < mb:
        msg = 'The minimum amount of memory for a package is 1MB but %r byte were reqested' % args.memory
        raise argparse.ArgumentTypeError(msg)
    if args.quota < gb:
        msg = 'The minimum amount of quote for a package is 1GB but %r byte were reqested' % args.quota
        raise argparse.ArgumentTypeError(msg)
    res = args.endpoint.create(args.name, int(args.memory/mb), int(args.quota/gb), args.cpu_cap, reqs)
    if args.p:
        if res:
            print res['uuid']
        else:
            exit(1)
    else:
        if res:
            print 'Pacakge successfully created: %s' % res['uuid']
        else:
            print 'Package creation failed: %r' % res
            exit(1)


def byte_size(string):
    scale_map = {
        'B': 1,
        'KB': 1024,
        'MB': 1024*1024,
        'GB': 1024*1024*1024,
        'TB': 1024*1024*1024*1024,
        'EB': 1024*1024*1024*1024*1024,
        'PB': 1024*1024*1024*1024*1024*1024,
    }
    p = re.compile('(\d+)(B|KB|MB|GB|TB|EB|PB)?')
    m = p.match(string)
    if not m:
        msg = '%r is not byte size. Use <number>[B|KB|MB|GB|TB|PB|EB]' % string
        raise argparse.ArgumentTypeError(msg)
    value = int(m.group(1))
    scale = m.group(2) or 'B'
    return value*scale_map[scale]

def package_rule(rule):
    weight = mk_weight(rule[0])
    attr = rule[1]
    cond = mk_cond(rule[2])
    val = mk_value(rule[3])
    return {
        'weight': weight,
        'condition': cond,
        'attribute': attr,
        'value': val
    }


def package_scale(scale):
    return {
        'weight': 'scale',
        'attribute': scale[0],
        'low': int(scale[1]),
        'high': int(scale[2])
    }

def package_random(rand):
    return {
        'weight': 'random',
        'low': int(scale[0]),
        'high': int(scale[1])
    }


def mk_weight(weight):
    if weight == 'must':
        return weight
    elif weight == 'cant':
        return weight
    else:
        return int(weight)

def mk_cond(cond):
    valid = ['>=', '|>', '=<', '<', '=:=', '=/=', 'subset', 'superset', 'disjoint', 'element']
    if not cond in valid:
        msg = '%r is not a valid condition, must be one of %r' % (cond, valid)
        raise argparse.ArgumentTypeError(msg)
    return cond;

def mk_value(val):
    num = re.compile('\d+')
    if num.match(val):
        return int(val)
    return val

class Package(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'packages'

    def create(self, name, ram, quota, cpu_cap, reqs):
        specs = {
            'name': name,
            'ram': ram,
            'quota': quota,
            'cpu_cap': cpu_cap
        }
        if reqs != []:
            specs['requirements'] = reqs
        return self._post(specs)

    def make_parser(self, subparsers):
        parser_pkgs = subparsers.add_parser('packages', help='package related commands')
        parser_pkgs.set_defaults(endpoint=self)
        subparsers_pkgs = parser_pkgs.add_subparsers(help='package commands')
        self.add_metadata_parser(subparsers_pkgs)
        parser_pkgs_list = subparsers_pkgs.add_parser('list', help='lists packages')
        parser_pkgs_list.add_argument('--fmt', action=ListAction, default=['uuid', 'name', 'ram', 'cpu_cap', 'quota'])
        parser_pkgs_list.add_argument('-H', action='store_false')
        parser_pkgs_list.add_argument('-p', action='store_true')
        parser_pkgs_list.set_defaults(func=show_list,
                                      fmt_def=pkg_fmt)
        parser_pkgs_get = subparsers_pkgs.add_parser('get', help='gets a package')
        parser_pkgs_get.add_argument('uuid')
        parser_pkgs_get.set_defaults(func=show_get)
        parser_pkgs_delete = subparsers_pkgs.add_parser('delete', help='deletes a package')
        parser_pkgs_delete.add_argument('uuid')
        parser_pkgs_delete.set_defaults(func=show_delete)
        parser_pkgs_create = subparsers_pkgs.add_parser('create', help='creates a new package')
        parser_pkgs_create.add_argument('-p', action='store_true',
                                        help='Output only shows the UUID no additional comments.')
        parser_pkgs_create.add_argument('--memory', '-m', required=True, type=byte_size,
                                        help='Amount of memory for the package.')
        parser_pkgs_create.add_argument('--quota', '-q', required=True, type=byte_size,
                                        help='Amount of quota for the package.')
        parser_pkgs_create.add_argument('--cpu_cap', '-c', required=True, type=int,
                                        help='Percentage of cores for the pacakge 100 = 1core.')
        parser_pkgs_create.add_argument('--requirement', '-r', action='append', nargs=4,
                                        help='Requirement rule <weight> <attr> <cond> <val>')
        parser_pkgs_create.add_argument('--scale', '-s', action='append', nargs=3,
                                        help='Scale rule <attr> <low> <hight>')
        parser_pkgs_create.add_argument('--random', '-R', action='append', nargs=2,
                                        help='Ramdom rule <low> <hight>')
        parser_pkgs_create.add_argument('name')
        parser_pkgs_create.set_defaults(func=create)
