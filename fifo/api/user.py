# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from .wiggle import Entity
from fifo.helper import *


user_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': '%36s', 'get': lambda e: d(e, ['uuid'])},
    'name':
    {'title': 'Name', 'len': 10, 'fmt': '%-10s', 'get': lambda e: d(e, ['name'])},
    'roles':
    {'title': 'Roles', 'len': 10, 'fmt': '%-10s', 'get': lambda e: str(d(e, ['roles']))},
    'orgs':
    {'title': 'Orgs', 'len': 10, 'fmt': '%-10s', 'get': lambda e: str(d(e, ['orgs']))},
}



def user_create(args):
    if not args.password:
        print 'You have to specify a passwrd'
        exit(1)
    wiggle = args.endpoint._wiggle
    reply = args.endpoint.create(args.name, args.password)
    if reply:
        if args.organization:
            args.endpoint.join_org(reply['uuid'], args.organization)
        if args.p:
            if reply:
                print reply['uuid']
            else:
                exit(1)
        else:
            if reply:
                print 'User successfully created: %s' % reply['uuid']
            else:
                print 'User creation failed: %r' % reply
                exit(1)
    else:
        print 'Faied to create VM.'

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

def user_delete(args):
    args.endpoint.delete(args.endpoint.uuid_by_name(args.uuid))

def sign_csr(args):
    if args.csr:
        f = open(args.csr, 'r')
        csr = f.read()
        f.close()
    else:
        csr = sys.stdin.read()
    uuid = args.endpoint.uuid_by_name(args.uuid)
    comment = args.comment
    #TODO: make scope configurable?
    scope = ["*"]
    r = args.endpoint.sign(uuid, comment, scope, csr)
    if r:
        print r["cert"]
        exit(0)
    else:
        print r
        exit(1)

class User(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = 'users'

    def create(self, name, password):
        return self._post({'user': name,
                           'password': password})

    def grant(self, user, permission):
        return self._put_attr(user, ['permissions'] + permission, {})

    def sign(self, uuid, comment, scope, csr):
        payload = {
            "scope": ["*"],
            "comment": comment,
            "csr": csr
        }
        return self._post_attr(uuid, 'tokens', payload)

    def join_org(self, uuid, org):
        return self._put_attr(uuid, 'orgs/' + org, {})

    def make_parser(self, subparsers):
        parser_users = subparsers.add_parser('users', help='user related commands')
        parser_users.set_defaults(endpoint=self)
        subparsers_users = parser_users.add_subparsers(help='user commands')
        self.add_metadata_parser(subparsers_users)
        parser_users_list = subparsers_users.add_parser('list', help='lists users')
        parser_users_list.add_argument('--fmt', action=ListAction,
                                       default=['uuid', 'name'])
        parser_users_list.add_argument('-H', action='store_false')
        parser_users_list.add_argument('-p', action='store_true')
        parser_users_list.set_defaults(func=show_list,
                                       fmt_def=user_fmt)
        parser_users_get = subparsers_users.add_parser('get', help='gets a user')
        parser_users_get.add_argument('uuid')
        parser_users_get.set_defaults(func=show_get)
        parser_users_sign = subparsers_users.add_parser('sign', help='sign a CSR and links the certificate.')
        parser_users_sign.add_argument('uuid', help="UUID of the user")
        parser_users_sign.add_argument('--csr', help="CSR file from openssl req command")
        parser_users_sign.add_argument('--comment', help="comment", default="SSL Cert")
        parser_users_sign.set_defaults(func=sign_csr)

        parser_users_delete = subparsers_users.add_parser('delete', help='gets a user')
        parser_users_delete.add_argument('uuid')
        parser_users_delete.set_defaults(func=show_delete)
        # fifo users create bill -p pass -g role -o org
        parser_users_create = subparsers_users.add_parser('create', help='creates a new user')
        parser_users_create.add_argument('name',
                                         help='Name of the user')
        parser_users_create.add_argument('-p', action='store_true')
        parser_users_create.add_argument('--password', '-P',
                                         help='Password of the user.')
        parser_users_create.add_argument('--role', '-g',
                                         help='Role of the user.')
        parser_users_create.add_argument('--organization', '-o',
                                         help='Organization of the user.')
        parser_users_create.set_defaults(func=user_create)
        parser_users_delete = subparsers_users.add_parser('delete', help='deletes a user')
        parser_users_delete.add_argument('uuid',
                                         help='uuid of VM to show')
        parser_users_delete.set_defaults(func=user_delete)
        parser_users_grant = subparsers_users.add_parser('grant', help='grants a permission to a user')
        parser_users_grant.add_argument('-p', action='store_true')
        parser_users_grant.add_argument('uuid')
        parser_users_grant.add_argument('permission', nargs='*')
        parser_users_grant.set_defaults(func=grant)
