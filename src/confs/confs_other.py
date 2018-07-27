#!/bin/env python3

from docopt import docopt

from confs.common import takesoptionals, config_from_options

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
