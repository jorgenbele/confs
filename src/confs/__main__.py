#!/bin/env python3

"""Confs

Usage: confs [options] <command> [<args>...]

Options:
  -v, --verbose
  -p, --pretty
  -t, --terse
  --path <path>

Commands:
  config (get <key> | set <key> <value> | show)
  add <identifier> <target_name> <target_dest>
  create <identifier>
  delete <identifier> NOT IMPLEMENTED
  enable <identifier>
  install <identifier> [<targets>...]
  migrate <identifier> <paths>...
  show [<identifiers>...]
  uninstall <typename> [<targets>...]
  tree
  examples

See confs(1) for more details.
"""

from docopt import docopt

from confs.common import fatal, verbose

def main():
    args = docopt(__doc__,
                  version='confs 0.1',
                  options_first=True)
    verbose('global arguments:')
    verbose(args)
    verbose('command arguments:')

    argv = [args['<command>']] + args['<args>']
    verbose(argv)

    cmd = args['<command>']
    cargs = args['<args>']

    if cmd == 'add':
        from confs.confs_add import add_cmd
        add_cmd(cargs)
    elif cmd == 'config':
        from confs.confs_config import config_cmd
        config_cmd(cargs)
    elif cmd == 'create':
        from confs.confs_create import create_cmd
        create_cmd(cargs)
    elif cmd == 'enable':
        from confs.confs_enable import enable_cmd
        enable_cmd(cargs)
    elif cmd == 'install':
        from confs.confs_install import install_cmd
        install_cmd(cargs)
    elif cmd == 'migrate':
        from confs.confs_migrate import migrate_cmd
        migrate_cmd(cargs)
    elif cmd == 'show':
        from confs.confs_show import show_cmd
        show_cmd(cargs)
    elif cmd == 'tree':
        from confs.confs_other import tree_cmd
        tree_cmd(cargs)
    elif cmd == 'uninstall':
        from confs.confs_uninstall import uninstall_cmd
        uninstall_cmd(cargs)
    elif cmd == 'examples':
        from confs.confs_other import examples_cmd
        examples_cmd(cargs)
    else:
        fatal('Unknown command `{}`'.format(args['<command>']))

if __name__ == '__main__':
    main()
