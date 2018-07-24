#!/bin/env python3

import os
import sys
from pathlib import Path
from docopt import docopt

from confs.confslib import *
import confs.confslib

from confs.common import *

@takesoptionals()
def enable_cmd(args):
    """Usage: confs [options] enable <identifier>"""
    args = docopt(enable_cmd.__doc__)
    config = config_from_options(args)
    print(args)

    typename, altname = split_identifier(args['<identifier>'])

    conf = load_conf(typename, config)
    err = conf.enable_alt_by_name(altname, write_now=True)
    if err:
        fatal('Unable to enable `{}`: {}'.format(args['<name>'], err))
    pprint('Enabled alt `{}` for type `{}`'.format(altname, typename), success=True)
