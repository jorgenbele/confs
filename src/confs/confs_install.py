#!/bin/env python3

"""
Usage: confs [options] install <identifier> [<targets>...]

Installs all, or only the specified targets of an alt specified by
<identifier> on the form <typename/altname>

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

from confs.common import *

def install_cmd(args):
    args = docopt(__doc__)
    config = config_from_options(args)
    print(args)

    typename, altname = split_identifier(args['<identifier>'], alt_optional=True)
    print('typename:', typename, 'altname:', altname)

    conf = load_conf(typename, config)
    # Uninstall the previous targets (if any)
    # NOTE: Currently uninstals regardless of whether
    # its also the one to be installed.
    if conf.enabled_alt:
        # TODO: only act on .save()
        err = conf.enabled_alt.uninstall(logfile=sys.stderr)
        if err:
            fatal('Failed to uninstall previously installed `{}/{}`: {}'.format(conf.name, conf.enabled_alt.name, err))
        pprint('Uninstalled previously installed `{}/{}`'.format(conf.name, conf.enabled_alt.name), success=True)
        
    # Enable (regardless of whether it is already enabled)
    err, alt = conf.get_alt_by_name(altname)
    if err:
        fatal('Unable to find alt `{}`: {}'.format(args['<identifier>'], err))
    err = conf.enable_alt_by_name(altname, write_now=True)
    if err:
        fatal('Unable to enable `{}`: {}'.format(args['<identifier>'], err))
    pprint('Enabled alt `{}` for type `{}`'.format(altname, typename), success=True)
    
    # Install targets
    if args['<targets>']:
        # Make sure all the specified targets exists.
        missing = []
        targetnames = [target.name for target in alt.targets]
        for targetname in args['<targets>']:
            if targetname not in targetnames:
                missing.append(targetname)
        if len(missing) > 0:
            fatal('Was unable to find targets for alt `{}`: {}'.format(altname, targetnames))
        # Do the install
        for target in alt.targets:
            if target.name in args['<targets>']:
                err = target.install()
                if err:
                    pprint('Installation of target `{}` failed. Skipping.', warning=True)
                verbose('Installed target: `{}`'.format(target.name))
    else:
        for target in alt.targets:
            err = target.install()
            if err:
                pprint('Installation of target `{}` failed. Skipping.', warning=True)
            verbose('Installed target: `{}`'.format(target.name))
        #err = alt.install()
        #if err:
        #    fatal('Installation of `{}` failed: {}'.format(args['<identifier>'], err))

    pprint('Installed `{}/{}`'.format(altname, typename), success=True)
