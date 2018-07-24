#!/bin/env python3

from pathlib import Path
import sys

from confs.confslib import ConfType, Config

from functools import wraps, partial


def takesoptionals(takes_path=False):
    optionals_str = """

Options:
    -v, --verbose       Verbose output
    -p, --pretty        Pretty output (formatted output)
    -t, --terse         Terse output (machine readable)"""

    if takes_path:
        optionals_str += """
        --path <path>   Set custom confs path
        """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wrapper.__doc__ += optionals_str
            return func(*args, **kwargs)
        return wrapper
    return decorator

def is_interactive():
    return sys.__stdout__.isatty()

class ArgFlags:
    pretty = False
    pretty_or_terse_flag_present = False
    verbose = False
    interactive = False

    @staticmethod
    def from_args(args):
        ArgFlags.interactive = is_interactive()
        for arg in [k for k, v in args.items() if v]: # only care about flags set to True
            if arg == '--pretty':
                ArgFlags.pretty = True
                ArgFlags.pretty_or_terse_flag_present = True
            elif arg == '--terse':
                ArgFlags.pretty = False
                ArgFlags.pretty_or_terse_flag_present = True
            elif arg == '--verbose':
                ArgFlags.verbose = True

        if not ArgFlags.pretty_or_terse_flag_present:
            # use --pretty implicitly when interactive
            ArgFlags.pretty = ArgFlags.interactive
    
def config_from_options(args):
    ArgFlags.from_args(args)
    config = Config()
    if '--path' in args and args['--path']:
        config.confs_path = args['--path']
    else:
        config.confs_path = '/home/jbr/.confs/'
    return config

def load_conf(name, config, ignore_error=True):
    p = Path(config.confs_path, name)
    err, conf = ConfType.from_conf_path(path=p, config=config)
    if err:
        if ignore_error:
            return None
        fatal('Unable to load confs: {}'.format(err))
    return conf
    
def load_confs(config):
    confs = []
    for p in Path(config.confs_path).iterdir():
        if p.stem not in config.excluded_conf_types:
            err, conf = ConfType.from_conf_path(path=p, config=config)
            if err:
                fatal('Unable to load confs: {}'.format(err))
            confs.append(conf)
    verbose('Loaded {} confs from `{}`'.format(len(confs), config.confs_path))
    return confs

def split_identifier(identifier, alt_optional=False):
    """
    Splits an identifier into (typename, altname), where
    altname may be None if kwarg alt_optional == True.
    """
    split = identifier.split('/')
    if len(split) > 2:
        fatal('Identifier `{}` is invalid! It cannot contain a `/`!'.format(identifier))
    elif len(split) < 1:
        fatal('Identifier `{}` is invalid!'.format(identifier))
        
    if alt_optional:
        if len(split) == 1:
            return (split[0], None)
        return tuple(split)
    else:
        if len(split) == 1:
            # was only typename, but altname is not optional
            fatal('Alt identifier `{}` is missing  alt name!'.format(identifier))
        return tuple(split)


def pprint(fargs, *args, word_wrap=True, warning=False, bold=False, success=False, enabled=False, fatal=False, header=False, **kwargs):
    def escape(s):
        return '\033{}'.format(s)

    """Pretty print"""
    if ArgFlags.pretty:
        bold_str = escape('[1m') if bold else ''
        color_str = ''
        reset_str = ''
        if warning or fatal:
            color_str = escape('[31m') # red
        elif success or enabled:
            color_str = escape('[32m') # green
        elif header:
            color_str = escape('[33m') # orange

        if bold or len(color_str) > 0:
            reset_str = escape('[0m') # none
            
        # TODO wordwrap
        nfargs = '{}{}{}'.format(bold_str, color_str, fargs)
        return print(nfargs, *args, reset_str, **kwargs)
    else:
        return print(fargs, *args, **kwargs)

def fatal(fargs, exit_code=1, *args, **kwargs):
    """Prints an error message and exits using exit_code"""
    pprint(fargs, fatal=True, file=sys.stderr, *args, **kwargs)
    sys.exit(exit_code)
    
def log(fargs, *args, **kwargs):
    pprint(fargs, file=sys.stderr, *args, **kwargs)

def verbose(fargs, *args, **kwargs):
    if ArgFlags.verbose:
        pprint(fargs, file=sys.stderr, *args, **kwargs)

def stringify(row):
    return [str(c) for c in row]

def align_columns(rows, column_options=None, spacing=1, header=None):
    """
    Aligns columns in a row of items.
    column_options is a list containing descibing how each column
    should be aligned
    Example: ['left', 'center', 'right'] will align the first column to the
    left, the second to the center, and the third to the right.
    """
    
    srows = []
    if header:
        srows.append(stringify(header))
    srows = srows + [stringify(row) for row in rows]

    column_details = {}
    for r in srows:
        for i, c in enumerate(r):
            if i not in column_details:
                column_details[i] = {'width': 0}
            column_details[i]['width'] = max(column_details[i]['width'], len(c))
            
    spacing_str = ' ' * spacing

    def align_row(row):
        nonlocal column_details, column_options
        out_columns = []
        for i, c in enumerate(row):
            align_chr = '<' # left-align by default
            if column_options:
                if column_options[i] == 'right':
                        align_chr = '>'
                elif column_options[i] == 'center':
                        align_chr = '^'
            out_columns.append('{0:{1}{2}}'.format(c, align_chr, column_details[i]['width']))
        return spacing_str.join(out_columns)

    out = []
    for r in srows:
        out.append(align_row(r))
    return out

    
def print_rows(rows, column_options=None, spacing=1, header=None, enabled_rows=set(), **kwargs):
    # TODO **kwargs
    # Only print header if pretty
    if len(rows) < 1:
        return False

    if ArgFlags.pretty:
        aligned = align_columns(rows=rows, column_options=column_options, spacing=spacing, header=header)
        #print(aligned)
        if header:
            pprint(aligned[0], header=True, **kwargs)
            aligned.pop(0)
        for i, row in enumerate(aligned):
            pprint(row, enabled=(i in enabled_rows), **kwargs)
    else:
        for row in rows:
            print('{}'.format(' '.join(stringify(row))))
            
    return True
