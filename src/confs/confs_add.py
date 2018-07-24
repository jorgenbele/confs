#!/bin/env python3

"""
Usage: confs [options] add <identifier> <target_name> <target_dest>

Options:
  -v, --verbose                 Verbose output
  -p, --pretty                  Pretty output (formatted output)
  -t, --terse                   Terse output (machine readable)
  --path <path>                 Set custom confs path
  -f, --is-file                 Create a file instead of a directory
                                  as the targets content. Useful for rc files.
Description:
  Adds a new target named <target_name> which installs to <target_dest>,
  to the alt identified by <identifier>.
"""

import os
import sys
from pathlib import Path
from docopt import docopt

from confs.confslib import *
import confs.confslib

from confs.common import *

def add_cmd(args):
    args = docopt(__doc__)
    config = config_from_options(args)
    verbose(args)

    typename, altname = split_identifier(args['<identifier>'])
    verbose('typename:', typename, 'altname:', altname)

    conf = load_conf(typename, config)
    err, alt = conf.get_alt_by_name(altname)
    if err:
        fatal('Unable to get `{}`: {}'.format(args['<identifier>'], err))

    # Add link to targets directory
    err = alt.add_target(args['<target_name>'], Path(args['<target_dest>']).absolute())
    if err:
        fatal('Unable to add target `{}` to `{}`: {}'.format(args['<target_name>'], args['<identifier>'], err))

    contents_path = Path(alt.path, args['<target_name>']).absolute()
    # Create file/directory
    if args['--is-file']:
        contents_path.touch()
    else:
        contents_path.mkdir()

    pprint('Added type `{}` to alt `{}`'.format(typename, altname), success=True)
