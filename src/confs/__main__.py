#!/bin/env python3

"""Confs

Usage: confs [options] <command> [<args>...]

Options:
  -v, --verbose         Verbose output
  -p, --pretty          Pretty output (formatted output)
  -t, --terse           Terse output (machine readable)
  --path <path>         Set custom confs path

Commands:
  config (get <key> | set <key> <value> | show)
  add <identifier> <target_name> <target_dest>  Add an alt
  create <typename>                Create a new config type
  enable <identifier>              Enable an alt
  examples                         Display usage examples
  show                             Show all config alts for the type
  tree                             Show a tree of the confs directory

  migrate <identifier> <paths>...  Migrates files from <paths>... 
                                   to an alt (<identifier>)

"""

from docopt import docopt

from confs.common import fatal, verbose, takesoptionals, config_from_options

def main():
    args = docopt(__doc__,
                  version='confs 0.1',
                  options_first=True)
    verbose('global arguments:')
    verbose(args)
    verbose('command arguments:')

    @takesoptionals(takes_path=True)
    def tree_cmd(args):
        """Usage: confs [options] tree"""
        args = docopt(tree_cmd.__doc__)
        config = config_from_options(args)
        import subprocess
        subprocess.run(['tree', '-a', '-L', '4', config.confs_path])


    def examples_cmd(args):
        examples = """# Adding vim configs to be managed by confs:
# Create conf type named 'vim'.
$ confs create vim
# Since no alt was provided, the 'default' alt was created.

# Migrate ~/.vim and ~/.vimrc into the vim/default alt
# to the new alt. --install automatically installs the alternative.
$ confs migrate vim/default ~/.vim ~/.vimrc

# Now that one can modify ~/.vim and ~/.vimrc as before, but its now managed by confs.
$ ls -al ~/.vim ~/.vimrc
drwxr-xr-x 1 user user 4096 Jan 01 01 00:01 ~/.vim   -> ~/.confs/vim/default/.vim
drwxr-xr-x 1 user user   30 Jan 01 01 00:01 ~/.vimrc -> ~/.confs/vim/default/.vimrc"""
        print(examples)
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
        tree_cmd(cargs)
    elif cmd == 'uninstall':
        from confs.confs_uninstall import uninstall_cmd
        uninstall_cmd(cargs)
    elif cmd == 'examples':
        examples_cmd(cargs)
    else:
        #if args['<command>'] in commands:
        #    commands[args['<command>']](args['<args>'])
        fatal('Unknown command `{}`'.format(args['<command>']))

if __name__ == '__main__':
    main()
