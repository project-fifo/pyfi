import argparse
import json
import re
from pprint import pprint

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
    r = []
    for k in args.fmt:
        r.append(args.fmt_def[k]['title'])
    if args.p:
        print(":".join(r))
    else:
        print(fmt % tuple(r))
    r = []
    if not args.p:
        for k in args.fmt:
            r.append("-" * args.fmt_def[k]['len'])
        print(fmt % tuple(r))

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


