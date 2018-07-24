#!/bin/env python3

import sys
from docopt import docopt

from confs.common import *
from confs.confslib import Config

def show_identifier(identifier, config):
    typename, altname = split_identifier(identifier, alt_optional=True)
    verbose('typename:', typename, 'altname:', altname)
    conf = load_conf(typename, config)

    if altname:
        for alt in conf.alts:
            if alt.name == altname:
                pprint('{}:'.format(identifier), header=True)
                # The first row element (''), together with the first element
                # in the header list ('   ') creates a ident which is only there
                # in pretty mode
                rows = [['', t.name, t.target, t.is_installed()] for t in alt.targets]
                enabled_rows = [i for i, row in enumerate(rows) if row[-1]]
                print_rows(rows=rows,
                           column_options=['left', 'left', 'left', 'left'],
                           spacing=2,
                           header=['   ', 'Name', 'Target dest', 'Installed'],
                           enabled_rows=enabled_rows)
                return
        fatal('Unable to find alt `{}`'.format(identifier))
    else:
        for alt in conf.alts:
            pprint('{}/{}:'.format(typename, alt.name), header=True)
            rows = [['', t.name, t.target, t.is_installed()] for t in alt.targets]
            enabled_rows = [i for i, row in enumerate(rows) if row[-1]]
            print_rows(rows=rows,
                       column_options=['left', 'left', 'left', 'left'],
                       spacing=2,
                       header=['   ', 'Name', 'Target dest', 'Installed'],
                       enabled_rows=enabled_rows)
    

@takesoptionals(takes_path=True)
def show_cmd(args):
    """Usage: confs [options] show [<identifiers>...]"""
    args = docopt(show_cmd.__doc__)
    config = config_from_options(args)
    verbose(args)

    confs = load_confs(config)
    verbose(confs)
    
    if args['<identifiers>']:
        for identifier in args['<identifiers>']:
            show_identifier(identifier, config)
        return

    rows = [[conf.name, conf.enabled_alt.name if conf.enabled_alt else '',
             len(conf.alts), 
             (conf.enabled_alt and any([t.is_installed() for t in conf.enabled_alt.targets]))] 
            for conf in confs]

    enabled_rows = [i for i, row in enumerate(rows) if row[-1]]
    print_rows(rows=rows, 
               column_options=['left', 'left', 'right', 'left'],
               spacing=2,
               header=['Type', 'Enabled alt', 'Num alts', 'Installed'],
               enabled_rows=enabled_rows)
