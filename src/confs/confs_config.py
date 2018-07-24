#!/bin/env python3
import os
import sys
from pathlib import Path
from docopt import docopt

from confs.confslib import *
import confs.confslib

from confs.common import *

@takesoptionals()
def config_cmd(args):
    """
    Usage: confs [options] config (get <key> | set <key> <value> | show)
    """
    args = docopt(config_cmd.__doc__, options_first=True)
    config = config_from_options(args)
    if args['get']:
        print(config.get(args['<key>']))
    elif args['set']:
        print(config.set(args['<key>'], args['<value>']), file=sys.stderr)
        ## TODO save changes to file?
    elif args['show']:
        print_rows(rows=[[k, v] for k, v in config.getall().items()], column_options=['left', 'left'], header=['Key', 'Value'])
