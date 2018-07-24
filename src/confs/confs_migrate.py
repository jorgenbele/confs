#!/bin/env python3

"""
Usage: confs [options] migrate <identifier> <paths>...

Options:
  -v, --verbose                 Verbose output
  -p, --pretty                  Pretty output (formatted output)
  -t, --terse                   Terse output (machine readable)
  --path <path>                 Set custom confs path          

Description:
   Moves ("migrates") a file/directory to a new target with the same name.
   This will have the same effect as creating a new target using method 1, 
   then moving from <migrate_path> to the new targets content path, followed
   by creating the symlink from <migrate_path> back to the content path 
  (eg. by using confs install ...).
"""

import os
import sys
from pathlib import Path
from docopt import docopt

from confs.confslib import *
import confs.confslib

from confs.common import *

def migrate_cmd(args):
    args = docopt(__doc__)
    config = config_from_options(args)
    print(args)
    
    typename, altname = split_identifier(args['<identifier>'])
    print('typename:', typename, 'altname:', altname)

    conf = load_conf(typename, config, ignore_error=False)
    err, alt = conf.get_alt_by_name(altname)
    if err:
        fatal('Unable to get `{}`: {}'.format(args['<identifier>'], err))

    
    print('Migrating: {}'.format(args['<paths>']))
    
    mpaths = [Path(p).absolute() for p in args['<paths>']]
    for mpath in mpaths:
        target_name = mpath.stem
        target_dest = mpath
        contents_path = Path(alt.path, target_name).absolute()

        err, target = alt.add_target(target_name, target_dest)
        if err:
            fatal('Unable to add (migrate) target `{}` from `{}`: {}'.format(target_name, target_dest, err))

        # Move file/dir at mpath to the contents path
        migrate_path = Path(mpath).absolute()
        migrate_path.rename(contents_path)

        # Create the symlink (install)
        err = target.install()
        resetErr = None
        if err:
            resetErr = err

        if not resetErr:
          err = alt.save()
          if err:
              resetErr = err

        if resetErr:
            # Reset changes
            # Move files back to original path
            migrate_path.rename(Path(mpath).absolute())
            # Delete target
            inner_err = alt.delete_target(targetname, write_now=True)
            if inner_err:
                fatal('Unable to delete target {} during resetting of changes from error: {}, {}'.format(targetname, inner_err, err))
            return 
            fatal('Unable to save (migrated) target `{}` from `{}`: {}'.format(target_name, target_dest, err))
        else:
            pprint('Migrated `{}` to `{}`'.format(mpath, args['<identifier>']), success=True)
