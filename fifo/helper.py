# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import print_function
import argparse
import json
import re
from pprint import pprint
import sys

# Verbose print support
# http://stackoverflow.com/questions/5980042/how-to-implement-the-verbose-or-v-option-into-a-script
# below is the 2.x version, may be change in for 3.x version python
_vprint = lambda *a, **k: None

def vprint(*args):
    _vprint("> ", end="", file=sys.stderr)
    _vprint(*args, file=sys.stderr)

def init_vprint(verbose):
    global _vprint
    _vprint = print if verbose else lambda *a, **k: None

# curl print support
_curlprintSwitch = False

def curlprint(host, method, path, headers, data=None, upload=None, file=None, fileMode="ascii"):
    if _curlprintSwitch:
        print("> [curl] ", end="", file=sys.stderr)
        headersp = ' '.join(map(lambda x: '-H "' + x +':' + headers[x] + '"', headers))
        datap = ''
        if data:
            datap = '-d ' + json.dumps(data)
        filep = ''
        if file:
            filep = '--data-' + fileMode + ' @' + file
        uploadp = ''
        if upload:
            uploadp = '-T ' + upload
        print("curl -X {method} http://{host}{path} {headers_params} {data_params} {upload_params} {file_params}".format(
            method=method,
            host=host,
            path=path,
            headers_params=headersp,
            data_params=datap,
            upload_params=uploadp,
            file_params=filep
        ), file=sys.stderr)

def init_curlprint(curl):
    global _curlprintSwitch
    _curlprintSwitch = curl

# We need to add a own action for lists as arguments
class ListAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values.split(','))

def is_uuid(str):
    regexp = '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    if re.match(regexp, str):
        return True
    else:
        return False

# Gets a value from a nested hash map or returns a given default if the value
# is not present
def d(o, p, deflt="-"):
    if p == []:
        return o
    else:
        k = p[0]
        if k in o:
            return d(o[k], p[1:], deflt)
        else:
            return deflt

# Helper function to generate a formatstring out of the format definition and the selected fields
def mk_fmt_str(args):
    s = ""
    for k in args.fmt:
        s = s + args.fmt_def[k]['fmt'] + " "
    return s

# Helper function to generate the format values for one of the lines.
def mk_fmt_line(args, e):
    r = []
    for k in args.fmt:
        r.append(args.fmt_def[k]['get'](e))
    return r

# Prints the header for a list opperation based on the selected format
def header(args):
    fmt = mk_fmt_str(args)
    hfmt = fmt.replace('d', 's')
    r = []
    for k in args.fmt:
        r.append(args.fmt_def[k]['title'])
    if args.p:
        print(":".join(r))
    else:
        print(hfmt % tuple(r))
    r = []
    if not args.p:
        for k in args.fmt:
            r.append("-" * args.fmt_def[k]['len'])
        print(hfmt % tuple(r))

# Shows the data when list was selected.
def show_list(args):
    l = args.endpoint.list()
    if not l and l != []:
        print("error!")
        exit(1)
    if args.H:
        header(args)
    fmt = mk_fmt_str(args)
    for e in l:
        if not e:
            print("error!")
            exit(1)
        l = mk_fmt_line(args, e)
        if args.p:
            print(":".join(l))
        else:
            print(fmt%tuple(l))

# Shows the data when get was selected, outputs it in JSON
def show_get(args):
    e = args.endpoint.get(args.uuid)
    if not e:
        print("error!")
        exit(1)
    if 'map_fn' in args:
        e = args.map_fn(e)
    print(json.dumps(e, sort_keys=True, indent=2, separators=(',', ': ')))


# Shows the data when get was selected, outputs it in JSON
def show_delete(args):
    if not args.endpoint.delete(args.uuid):
        print("Failed to delete " + args.uuid)
        exit(1)
    print(args.uuid + " deleted successful.")

