#!/bin/env python3

"""
Usage: confs [options] create <identifier>

Creates a new type if <name> is a typename, or alt if <identifier>
is on the form <<typename>/<altname>>.

Options:
  -v, --verbose         Verbose output
  -p, --pretty          Pretty output (formatted output)
  -t, --terse           Terse output (machine readable)
  --path <path>         Set custom confs path          
"""

import os
import sys
from pathlib import Path
from docopt import docopt

from confs.confslib import *
import confs.confslib

from confs.common import *

def create_cmd(args):
    args = docopt(__doc__)
    config = config_from_options(args)
    print(args)
    
    typename, altname = split_identifier(args['<identifier>'], alt_optional=True)
    print('typename:', typename, 'altname:', altname)
    
    confs = load_confs(config)
    if not altname and typename in [conf_type.name for conf_type in confs]:
        fatal('Conf type `{}` already exists!'.format(typename))
        
    typepath = Path(config.confs_path, typename)
    conf_type = None

    if altname:
        # <identifer> was on the form <typename>/<altname>,
        # try to load the conf_type, or fall back
        # to creating it.
        conf_type = load_conf(typename, config, ignore_error=True)
    else:
        altname = 'default'
        
    loaded_type = False 
    if conf_type:
        loaded_type = True
        
    if not conf_type:
        conf_type = ConfType(name=typename, config=config, path=typepath)
    err, alt = conf_type.create_alt(altname, write_now=False)
    if err:
        fatal('Unable to create alt `{}/{}`: {}'.format(typename, altname, err))
        
    if not conf_type.enabled_alt:
        conf_type.enabled_alt = alt
    
    err = conf_type.save()
    if err:
        fatal('Unable to save target `{}`: {}'.format(typename, err))
        
    if not loaded_type:
        pprint('Created type `{}`'.format(typename), success=True)
    pprint('Created `{}/{}`'.format(typename, altname), success=True)
