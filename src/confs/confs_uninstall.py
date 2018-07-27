#!/bin/env python3

"""
Usage: confs [options] uninstall <typename> [<targets>...]

Uninstalls all, or only the specified targets, of the 
enabled alt for <typename>.

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

def uninstall_cmd(args):
    args = docopt(__doc__)
    config = config_from_options(args)
    verbose(args)
    
    conf = load_conf(args['<typename>'], config)
    # Uninstall the previous targets (if any)
    # NOTE: Currently uninstals regardless of whether
    # its also the one to be installed.
    if not conf:
        pprint('Conf type `{}` does not exist!'.format(args['<typename>']), warning=True)
        return
    elif not conf.enabled_alt:
        pprint('Conf type `{}` is not installd!'.format(conf.name), warning=True)
        return
        
    def uninstall_target(target):
      if not target.is_installed():
          verbose('Skipping target `{}`, not installed!'.format(target.name))
          return

      err = target.uninstall()
      if err:
          pprint('Uninstallation of target `{}` failed. Skipping.', warning=True)
      verbose('Uninstalled target: `{}`'.format(target.name))
      
    # Uninstall the desired targets
    if args['<targets>']:
        # Make sure all the specified targets exists.
        missing = []
        targetnames = [target.name for target in conf.enabled_alt.targets]
        for targetname in args['<targets>']:
            if targetname not in targetnames:
                missing.append(targetname)
        if len(missing) > 0:
            fatal('Was unable to find targets for alt `{}`: {}'.format(conf.enabled_alt.name, targetnames))
        # Do the uninstall
        for target in conf.enabled_alt.targets:
            if target.name in args['<targets>']:
                uninstall_target(target)
    else:
        for target in conf.enabled_alt.targets:
            uninstall_target(target)

    pprint('Uninstalled `{}/{}`'.format(conf.enabled_alt.name, args['<typename>']), success=True)
