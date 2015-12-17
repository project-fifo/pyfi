# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import ssl
import httplib
import json
import time
import copy
import urllib
from pprint import pprint
from fifo.helper import *

class Wiggle:
    def __init__(self):
        self._token = False
        self._apiEndpoint = '/api/2/'

    def init(self, host, user, pw, token, apiVersion, unsafe):
        self.host = host
        self.unsafe = unsafe
        self.headers = {'content-type': 'application/json;charset=UTF-8',
                        'accept': 'application/json'}
        self._apiVersion = '0.1.0'
        if apiVersion:
            self._apiVersion = apiVersion
            self._apiEndpoint = '/api/' + apiVersion + '/'
        if token:
            if not self.set_token(token):
                self.connect(user, pw)
        else:
            self.connect(user, pw)

    def conn(self):
        if self.unsafe:
            return httplib.HTTPConnection(self.host)
        else:
            return httplib.HTTPSConnection(self.host, context=ssl.create_default_context())

    def get_token(self):
        return self._token

    def set_token(self, token):
        self._token = token
        self.headers['X-Snarl-Token'] = self._token
        return self.get('sessions', token)

    def get(self, resource, entity, suffix='', rawResponse=False, headers=None):
        conn = self.conn()
        hdrs = headers or self.headers
        vprint('GET', self._apiEndpoint + resource + '/' + entity + suffix, '', hdrs)
        curlprint(self.host, 'GET', self._apiEndpoint + resource + '/' + entity + suffix, hdrs)
        conn.request('GET', self._apiEndpoint + resource + '/' + entity + suffix, '', hdrs)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status != 200):
            return False
        else:
            if rawResponse:
                return response
            else:
                return json.loads(response.read())

    def delete(self, resource, entity):
        conn = self.conn()
        vprint('DELETE', self._apiEndpoint + resource + '/' + entity, '', self.headers)
        curlprint(self.host, 'DELETE', self._apiEndpoint + resource + '/' + entity, self.headers)
        conn.request('DELETE', self._apiEndpoint + resource + '/' + entity, '', self.headers)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status >= 200 and response.status < 300):
            return True
        else:
            return False

    def delete_body(self, resource, entity, body):
        conn = self.conn()
        jbody = json.dumps(body)
        vprint('DELETE', self._apiEndpoint + resource + '/' + entity, jbody, self.headers)
        curlprint(self.host, 'DELETE', self._apiEndpoint + resource + '/' + entity, headers=self.headers, data=jbody)
        conn.request('DELETE', self._apiEndpoint + resource + '/' + entity, jbody, self.headers)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status >= 200 and response.status < 300):
            return True
        else:
            return False

    def delete_attr(self, resource, entity, attr):
        conn = self.conn()
        if isinstance(attr, str):
            attr = [attr]
        url = self._apiEndpoint + resource + '/' + entity + '/' + '/'.join(attr)
        vprint('DELETE', url, '', self.headers)
        curlprint(self.host, 'DELETE', url, headers=self.headers)
        conn.request('DELETE', url, '', self.headers)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status < 300 and response.status >= 300):
            return False
        else:
            return True

    def delete_attr_body(self, resource, entity, attr, body):
        conn = self.conn()
        if isinstance(attr, str):
            attr = [attr]
        url = self._apiEndpoint + resource + '/' + entity + '/' + '/'.join(attr)
        jbody = json.dumps(body)
        vprint('DELETE', url, jbody, self.headers)
        curlprint(self.host, 'DELETE', url, headers=self.headers, data=jbody)
        conn.request('DELETE', url, jbody, self.headers)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status < 300 and response.status >= 300):
            return False
        else:
            return True

    def put_attr(self, resource, entity, attr, body):
        conn = self.conn()
        if isinstance(attr, str):
            attr = [attr]
        jbody = json.dumps(body)
        url = self._apiEndpoint + resource + '/' + entity + '/' + '/'.join(attr)
        vprint('PUT', url, jbody, self.headers)
        curlprint(self.host, 'PUT', url, headers=self.headers, data=jbody)
        conn.request('PUT', url, jbody, self.headers)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status > 200 and response.status <= 400):
            return True
        else:
            return False

    def post_attr(self, resource, entity, attr, body):
        conn = self.conn()
        if isinstance(attr, str):
            attr = [attr]
        url = self._apiEndpoint + resource + '/' + entity + '/' + '/'.join(attr)
        jbody = json.dumps(body)
        vprint('POST', url, jbody, self.headers)
        curlprint(self.host, 'POST', url, headers=self.headers, data=jbody)
        conn.request('POST', url, jbody, self.headers)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status == 303):
            newurl = response.getheader('Location')
            conn = self.conn()
            conn.request('GET', newurl, '', self.headers)
            response = conn.getresponse()
            vprint('Status (after redirect): ', response.status)
            if (response.status == 404):
                time.sleep(5)
                conn = self.conn()
                conn.request('GET', newurl, '', self.headers)
                response = conn.getresponse()
                vprint('Status (after reload): ', response.status)
                if (response.status != 200):
                    return False
                else:
                    return json.loads(response.read())
            elif (response.status != 200):
                return False
            else:
                return json.loads(response.read())
        elif (response.status == 201):
            return 201
        elif (response.status == 200):
            return json.loads(response.read())
        else:
            return False

    def get_attr(self, resource, entity, attr):
        conn = self.conn()
        if isinstance(attr, str):
            attr = [attr]
        url = self._apiEndpoint + resource + '/' + entity + '/' + '/'.join(attr)
        vprint('GET', url, '', self.headers)
        curlprint(self.host, 'GET', url, headers=self.headers)
        conn.request('GET', url, '', self.headers)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status != 200):
            return False
        else:
            return json.loads(response.read())

    def put(self, resource, entity, body):
        conn = self.conn()
        if isinstance(entity, str):
            entity = [entity]
        url = self._apiEndpoint + resource + '/' + '/'.join(entity)
        jbody = json.dumps(body)
        vprint('PUT', url, jbody, self.headers)
        curlprint(self.host, 'PUT', url, headers=self.headers, data=jbody)
        conn.request('PUT', url, jbody, self.headers)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status != 200):
            return False
        else:
            return json.loads(response.read())

    def put_bindata(self, resource, entity, file, suffix='', headers=None):
        conn = self.conn()
        if isinstance(entity, str):
            entity = [entity]
        url = self._apiEndpoint + resource + '/' + '/'.join(entity) + suffix
        hdrs = headers or self.headers
        vprint('PUT', url, '@' + file.name, hdrs)
        curlprint(self.host, 'PUT', url, headers=hdrs, upload=file.name)
        conn.request('PUT', url, file, hdrs)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status > 200 and response.status > 200):
            return response.status
        if (response.status != 200):
            return False
        else:
            return json.loads(response.read())

    def post(self, resource, body):
        conn = self.conn()
        if isinstance(resource, str):
            resource = [resource]
        url = self._apiEndpoint + '/'.join(resource)
        jbody = json.dumps(body)
        vprint('POST', url, jbody, self.headers)
        curlprint(self.host, 'POST', url, headers=self.headers, data=jbody)
        conn.request('POST', url, jbody, self.headers)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status == 303):
            newurl = response.getheader('Location')
            conn = self.conn()
            conn.request('GET', newurl, '', self.headers)
            response = conn.getresponse()
            if (response.status != 200):
                print response.status
                return False
            else:
                return json.loads(response.read())
        elif (response.status == 200):
            return json.loads(response.read())
        else:
            print response.status
            return False

    def post_bindata(self, resource, entity, file, headers=None):
        conn = self.conn()
        if isinstance(resource, str):
            resource = [resource]
        url = self._apiEndpoint + '/'.join(resource) + '/' + entity
        hdrs = headers or self.headers
        vprint('POST', url, '@' + file.name, hdrs)
        curlprint(self.host, 'POST', url, headers=hdrs, file=file.name, fileMode='binary')
        conn.request('POST', url, file, hdrs)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status == 303):
            newurl = response.getheader('Location')
            conn = self.conn()
            conn.request('GET', newurl, '', self.headers)
            response = conn.getresponse()
            if (response.status != 200):
                print response.status
                return False
            else:
                return json.loads(response.read())
        elif (response.status == 200):
            return json.loads(response.read())
        else:
            print response.status
            return False

    def list(self, resource):
        conn = self.conn()
        vprint('GET', self._apiEndpoint + resource, '', self.headers)
        curlprint(self.host, 'GET', self._apiEndpoint + resource, headers=self.headers)
        conn.request('GET', self._apiEndpoint + resource, '', self.headers)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status != 200):
            return False
        else:
            return json.loads(response.read())

    def full_list(self, resource, fields):
        conn = self.conn()
        hdrs = self.headers
        hdrs['x-full-list'] = 'true'
        if fields != []:
            hdrs['x-full-list-fields'] = ','.join(fields)
        vprint('GET', self._apiEndpoint + resource, '', hdrs)
        curlprint(self.host, 'GET', self._apiEndpoint + resource, headers=hdrs)
        conn.request('GET', self._apiEndpoint + resource, '', hdrs)
        response = conn.getresponse()
        vprint('Status: ', response.status)
        if (response.status != 200):
            return False
        else:
            return json.loads(response.read())

    def connect(self, user, pw):
        conn = self.conn()
        if self._apiVersion == '0.1.0':
            vprint("WARNING OLD LOGIN")
            jbody = json.dumps({'user':user, 'password': pw})
            vprint('POST', self._apiEndpoint + 'sessions',  jbody, self.headers)
            curlprint(self.host, 'POST', self._apiEndpoint + 'sessions', headers=self.headers, data=jbody)
            conn.request('POST', self._apiEndpoint + 'sessions',  jbody, self.headers)
            response = conn.getresponse()
            vprint('Status:', response.status)
            if (response.status == 303):
                self._token = response.getheader('X-Snarl-Token')
                self.headers['X-Snarl-Token'] = self._token
                return self._token
            else:
                return False
        else:
            form = urllib.urlencode({'username' :user, 'password': pw, 'grant_type': 'password'})
            url = self._apiEndpoint + 'oauth/token'
            headers = copy.copy(self.headers)
            headers['content-type'] = 'application/x-www-form-urlencoded'
            vprint('POST', url, form, self.headers)
            curlprint(self.host, 'POST', url, headers=self.headers, data=form)
            conn.request('POST', url, form, self.headers)
            response = conn.getresponse()
            vprint('Status:', response.status)
            if (response.status == 200):
                resp = json.loads(response.read())
                self._token = resp['access_token']
                self.headers['authorization'] = 'Bearer ' + self._token
                return self._token
            else:
                return False


class Cloud:
    def __init__(self, wiggle):
        self._wiggle = wiggle
    def status(self):
        return self._wiggle.list('cloud')
    def connection(self):
        return self._wiggle.get('cloud', 'connection')

class Entity:
    def __init__(self, wiggle):
        self._resource = 'none'
        self._wiggle = wiggle
        self._fields = []

    def _put(self, uuid, body):
        uuid = self.uuid_by_name(uuid)
        return self._wiggle.put(self._resource, uuid, body)

    def _post(self, body):
        return self._wiggle.post(self._resource, body=body)

    def _put_file(self, entity, target, file):
        hdrs = dict(self._wiggle.headers)
        hdrs['Content-Type'] = 'application/x-gzip'
        return self._wiggle.put_bindata(self._resource, entity, headers=hdrs, suffix=target, file=file)

    def _post_file(self, entity, file):
        return self._wiggle.post_bindata(self._resource, entity, file=file)

    def _post_attr(self, uuid, entity, body):
        uuid = self.uuid_by_name(uuid)
        return self._wiggle.post_attr(self._resource, uuid, entity, body)

    def _put_attr(self, uuid, entity, body):
        uuid = self.uuid_by_name(uuid)
        return self._wiggle.put_attr(self._resource, uuid, entity, body)

    def _delete_attr(self, uuid, entity):
        uuid = self.uuid_by_name(uuid)
        return self._wiggle.delete_attr(self._resource, uuid, entity)

    def _delete_attr_body(self, uuid, entity, body):
        uuid = self.uuid_by_name(uuid)
        return self._wiggle.delete_attr_body(self._resource, uuid, entity, body)

    def _get_attr(self, uuid, attr):
        uuid = self.uuid_by_name(uuid)
        return self._wiggle.get_attr(self._resource, uuid, attr)

    def name_of(self, obj):
        return obj['name']

    def uuid_by_name(self, name):
        if is_uuid(name):
            return name
        else:
            for uuid in self.list():
                obj = self.get(uuid)
                if self.name_of(obj) == name:
                    return uuid
            return False

    def full_list(self, fields):
        return self._wiggle.full_list(self._resource, fields)

    def list(self):
        if not hasattr(self, '_fields'):
            self._fields = []
        return self._wiggle.full_list(self._resource, self._fields)

    def get(self, uuid):
        uuid = self.uuid_by_name(uuid)
        return self._wiggle.get(self._resource, uuid)

    def delete(self, uuid):
        uuid = self.uuid_by_name(uuid)
        return self._wiggle.delete(self._resource, uuid)

    def delete_body(self, uuid, body):
        uuid = self.uuid_by_name(uuid)
        return self._wiggle.delete_body(self._resource, uuid, body)

    def get_bindata(self, uuid, target, accept=''):
        uuid = self.uuid_by_name(uuid)
        binHeaders = dict(self._wiggle.headers)
        if accept:
            binHeaders['accept'] = accept
        else:
            del binHeaders['accept']
        return self._wiggle.get(self._resource, uuid, suffix=target, rawResponse=True, headers=binHeaders)

    def get_metadata(self, uuid):
        uuid = self.uuid_by_name(uuid)
        return self._wiggle.get_attr(self._resource, uuid, 'metadata')

    def set_metadata(self, uuid, path, k, v):
        uuid = self.uuid_by_name(uuid)
        path.insert(0, 'metadata')
        return self._wiggle.put_attr(self._resource, uuid, path, {k: v})

    def delete_metadata(self, uuid, path):
        uuid = self.uuid_by_name(uuid)
        path.insert(0, 'metadata')
        return self._wiggle.delete_attr(self._resource, uuid, path)

    def add_metadata_parser(self, subparsers):
        parser_metadata = subparsers.add_parser('metadata', help='Metadata commands')
        parser_metadata.add_argument('uuid', help='uuid of the element to look at')
        subparsers_metadata = parser_metadata.add_subparsers(help='Metadata commands')

        parser_mdata_get = subparsers_metadata.add_parser('get', help='get metadata')
        parser_mdata_get.set_defaults(func=mdata_get)

        parser_mdata_set = subparsers_metadata.add_parser('set', help='set metadata')
        parser_mdata_set.set_defaults(func=mdata_set)
        parser_mdata_set.add_argument('key', help='key of the metadata')
        group = parser_mdata_set.add_mutually_exclusive_group()
        group.add_argument('--integer', '-i', help='value is integer ', action='store_true')
        group.add_argument('--float', '-f', help='value is float', action='store_true')
        group.add_argument('--string', '-s', help='value is string', action='store_true')
        group.add_argument('--json', '-j', help='value is json', action='store_true')
        parser_mdata_set.add_argument('value', help='value to be set')
        parser_mdata_del = subparsers_metadata.add_parser('delete', help='deletes metadata')
        parser_mdata_del.set_defaults(func=mdata_delete)
        parser_mdata_del.add_argument('key', help='key of the metadata')


def mdata_get(args):
    e = args.endpoint.get(args.uuid)
    if not e or not e.has_key('metadata'):
        exit(1)
    services = e['metadata']
    print(json.dumps(services, sort_keys=True, indent=2, separators=(',', ': ')))

def mdata_set(args):
    keys = args.key.split('.')
    k = keys.pop()
    value = args.value
    if args.integer:
        value = int(args.value)
    elif args.float:
        value = float(args.value)
    elif args.json:
        value = json.loads(args.value)
    if args.endpoint.set_metadata(args.uuid, keys, k, value):
        print 'Metadata successfully updated!'
    else:
        print 'Failed to update metadata!'
        exit(1)

def mdata_delete(args):
    keys = args.key.split('.')
    if args.endpoint.delete_metadata(args.uuid, keys):
        print 'Metadata successfully updated!'
    else:
        print 'Failed to update metadata!'
        exit(1)
