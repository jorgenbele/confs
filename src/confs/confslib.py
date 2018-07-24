#!/bin/env python3
# File: confs1.py
# Author: Jørgen Bele Reinfjell
# Date: 15.07.2018 [dd.mm.yyyy]
# Description: Configuration file switcher

"""
 Example confs file structure with types 'vimrc' and 'bashrc' :
 / ($HOME/.confs)
 |---> vim/
 |     |---> enabled --> testing/
 |     |
 |     |---> testing/
 |     |     |---> targets/
 |     |     |     |---> vimrc --> "$HOME/.vimrc"
 |     |     |     \---> vim   --> "$HOME/.vim"
 |     |     |---> vimrc/
 |     |     \---> vim/
 |     |
 |     |---> stable/
 |     |     |---> targets/
 |     |     |     |---> vimrc --> "$HOME/.vimrc"
 |     |     |     \---> vim   --> "$HOME/.vim"
 |     |     |---> vimrc/
 |     |     \---> vim/
 |     |
 |     |---> peerprogramming/
 |     |     |---> targets/
 |     |     |     |---> vimrc --> "$HOME/.vimrc"
 |     |     |     \---> vim   --> "$HOME/.vim"
 |     |     |---> vimrc/
 |     |     \---> vim/
"""
import sys
import os
import argparse
from pathlib import Path
    
class Err:
    """Class used to represent Go-like errors."""
    def __init__(self, msg):
        self.msg = '{}: {}'.format(type(self).__name__, msg)
        
    def __str__(self):
        return str(self.msg)
    
    def __repr__(self):
        return '''<{} msg="{}">'''.format(type(self).__name__, self.__str__())
    
class MkdirErr(Err):
    pass
class MkLinkErr(Err):
    pass
class ExpDirErr(Err):
    pass
class ExpSymlinkErr(Err):
    pass
class InvTypenameErr(Err):
    pass
class InvOperErr(Err):
    pass
class InvTargetPathErr(Err):
    pass
class InvSymlinkErr(Err):
    pass
class IncDataErr(Err):
    pass
class InvAltNameErr(Err):
    pass
class InvTargetNameErr(Err):
    pass

class Config:
    confs_path = Path(Path.home(), '.confs') # The path to store the configs in
    enabled_link_name = 'enabled'            # The name to use for the 'enabled' symlink
    targets_dir_name = 'targets'             # The directory containing targets
    excluded_conf_types = ['.git']           # ConfType names to exclude
    excluded_alts = ['.git', enabled_link_name] # Alt names to exclude
    excluded_altfiles = ['.git']    # Alt filenames to exclude
    
    use_colors = True
    
    def __init__(self, confs_path=confs_path, excluded_conf_types=excluded_conf_types, 
                 excluded_alts=excluded_alts, excluded_altfiles=excluded_altfiles, 
                 enabled_link_name=enabled_link_name, targets_dir_name=targets_dir_name,
                 use_colors=use_colors):
        self.confs_path = confs_path
        self.excluded_conf_types = excluded_conf_types
        self.excluded_alts = excluded_alts
        self.excluded_altfiles = excluded_altfiles
        self.enabled_link_name = enabled_link_name
        self.targets_dir_name = targets_dir_name
        self.use_colors = use_colors
        
    
    def getall(self):
        return vars(self)
        
    def get(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            return None
    
    def set(self, key, val):
        # Refuse to set if the value does not already exist
        try:
            getattr(self, key)
        except AttributeError:
            return False

        try:
            setattr(self, key, val)
        except AttributeError:
            return False
        return True
        

class ConfType:
    def __init__(self, name: str, enabled_alt=None, alts=[], config: Config = Config(), path=None):
        self.name = name                # The name of the type (eg. vim)
        self.enabled_alt = enabled_alt  # The Alt instance that is the enabled alternative
        self.alts = alts                # The list of Alt instances which this ConfType contains
        self.config = config            # The config options used
        self.path = path                # The path to the current ConfType
    
    def __repr__(self):
        return '<ConfType name="{}" alts="{}" enabled_alt="{}">'.format(self.name, self.alts, self.enabled_alt) 
    
    def exists(self) -> bool:
        """
        Returns True if the ConfType itself exists 
        in the filesystem, else False.
        """
        return self.path.exists() if self.path else False
    
    def get_alt_by_name(self, altname: str):
        for alt in self.alts:
            if alt.name == altname:
                return (None, alt)
        return (InvAltNameErr('Unable to find alt `{}` in conf `{}`'
                              .format(altname, self.name)), None)
    
    def enable_alt_by_name(self, altname: str, write_now=True):
        """
        Enables an alt by setting the enabled symlink to link to it, 
        by default no write is done, but if write_now is specified, self.save() is called.
        """
        err, alt = self.get_alt_by_name(altname)
        if err:
            return err
        self.enabled_alt = alt
        if write_now:
            return self.save()
        return None
        
    def create_alt(self, altname: str, write_now=True):
        """
        Adds an alt to the list of alts. If write_now == False, then no 
        write is done before a call to self.save().
        """
        if not self.alts:
            self.alts = []
            
        # TODO: Verify when write_now == False
        alt = Alt(name=altname, conf_type=self, config=self.config)
        if write_now:
            err = alt.save()
            if err:
                return err, None
        self.alts.append(alt)
        return None, alt
        

    def save(self) -> Err:
        """
        Save the ConfType by creating the necessary 
        directories, files and links.
        """
        if self.name in self.config.excluded_conf_types:
            return InvTypenameErr('Type name `{}` invalid (in excluded list)'.format(self.name))

        # Create the config type directory itself if needed
        if not self.exists():
            if not self.path:
                self.path = Path(self.config.confs_path, self.name)
            try:
                self.path.mkdir()
            except PermissionError as pe:
                return PermErr('Permission error for `{}`: `{}``'.format(self.name, pe))

        # Save all alts
        for alt in self.alts:
            err = alt.save()
            if err:
                return err
            
        # Update the enabled symlink, potentially removing it
        enabled_path = Path(self.path, self.config.enabled_link_name).absolute()
        enabled_target = Path(self.path, enabled_path.resolve().stem).absolute() if enabled_path.is_symlink() else None
        
        if enabled_path.exists() and not enabled_target:
            # It exists, but is not a symlink. Error.
            return ExpSymlinkErr('`{}` is not a symlink!'.format(enabled_path))

        new_enabled_target = None
        if self.enabled_alt:
            new_enabled_target = self.enabled_alt.path.absolute()
            
        if new_enabled_target != enabled_target:
            # Target has changed.
            if enabled_path and enabled_path.exists():
                # Unlink if it exists
                enabled_path.unlink()
            if new_enabled_target:
                # Only symlink if not None
                enabled_path.symlink_to(new_enabled_target)
        return None
        
    @staticmethod
    def from_conf_path(path: Path, config: Config = Config()):
        """
        Returns a ConfType instances 
        instantiated from a filesystem path.
        """
        enabled_path = Path(path, config.enabled_link_name)
        if not enabled_path.exists():
            return (MkLinkErr('Enabled symlink not found: `{}`'.format(enabled_path)), None)
        elif not enabled_path.is_symlink():
            return (ExpSymlinkErr('Enabled-file is not a symlink: `{}`'.format(enabled_path)), None)
        enabled_resolved_stem = enabled_path.resolve().stem
        
        alts = []
        enabled_alt = None
        for p in path.iterdir():
            if not p.is_dir():
                log('Skipping alt `{}`, as it is not a directory!'.format(p.stem))
                continue
            if p.stem in config.excluded_alts:
                #log('Skipping alt `{}`, as it is in the excluded alts list!'.format(p.stem))
                continue

            err, alt = Alt.from_alt_path(p, config=config)
            if err:
                return (Err('Alt `{}` at `{}` is invalid: `{}`, skipping!'.format(p.stem, p, err)), None)
            else:
                if p.stem == enabled_resolved_stem:
                    enabled_alt = alt
                alts.append(alt)
        return (None, ConfType(path.stem, enabled_alt=enabled_alt, alts=alts, config=config, path=path))

class Alt:
    def __init__(self, name: str, conf_type=None, contents=[], missing_contents=[], targets=[], config: Config = Config(), path=None, **kwargs):
        self.name = name      # The alt name
        self.config = config  # The config to use
        self.contents = contents
        self.missing_contents = missing_contents
        self.targets = targets
        self.conf_type = conf_type
        self.path = path
        
    def __repr__(self):
        return '<Alt name="{}" contents="{}" missing_contents="{}" conf_type="{}" targets="{}">'.format(
            self.name, self.contents, self.missing_contents, self.conf_type, self.targets
        )
    
    def add_target(self, name: str, target: Path):
        """Adds a new target to the alt"""
        target_path = Path(self.path, self.config.targets_dir_name, name)
        target = Target(name=name, target=target, path=target_path, alt=self, config=self.config)
        err = target.save()
        if err:
            return err, None
        self.targets.append(target)
        return None, target
    
    # TODO add test
    def get_target_by_name(self, name):
        for t in self.targets:
            if t.name == name:
                return (None, t)
        return (InvTargetNameErr('No such target: `{}`'.format(name)), None)

    # TODO add test
    def delete_target(self, name: str, target: Path, write_now=False):
        """Removes a target from the alt """
        err, target = self.get_target_by_name(name)
        if err:
            return err
        err = target.delete(write_now=True)
        if err:
            return err
        self.targets.remove(target)
        if write_now:
            return self.save()
        return None, target
    
    def install(self, logfile=None):
        """Install/set symlinks as defined by self.targets."""
        for target in self.targets:
            # assume that contents are in this directory (at self.path)
            #content_path = Path(self.path, target.name)
            if logfile:
                print('Installing target: `{}` --> `{}`'.format(target.name, target.target), file=logfile)
            err = target.install()
            if err:
                return err
        return None

    def uninstall(self, logfile=None):
        """Uninstall/remove symlinks as defined by self.targets."""
        for target in self.targets:
            # assume that contents are in this directory (at self.path)
            if not target.is_installed():
                if logfile:
                    print('Skipping uninstalling target: `{}` --> `{}`, not installed'.format(target.name, target.target), file=logfile)
                continue
            if logfile:
                print('Uninstalling target: `{}` --> `{}`'.format(target.name, target.target), file=logfile)
            err = target.uninstall()
            if err:
                return err
        return None
    
    def save(self) -> Err:
        """Saves the alt"""
        # Set path from config if not yet set.
        if not self.path:
            self.path = Path(self.conf_type.path, self.name)
            
        # Create directory for the current alt if not yet created
        if not self.path.is_dir():
            if self.path.exists():
                # Path exists, but is not a directory.
                # Continuing could result in data loss.
                return ExpDirErr('Alt path `{}` is not a directory'.format(self.path))

            try:
                self.path.mkdir()
            except PermissionError as pe:
                return MkdirErr('Could not create directory `{}`: `{}`!'
                                 .format(self.path, pe))
        
        # Create directory for targets if not yet existing
        targets_path = Path(self.path, self.config.targets_dir_name)
        if not targets_path.is_dir():
            if targets_path.exists():
                return ExpDirErr('Targets path `{}` is not a directory'.format(self.path))

            try:
                targets_path.mkdir()
            except PermissionError as pe:
                return MkdirErr('Could not create directory `{}`: `{}`!'
                                 .format(targets_path, pe))

        # Save all targets
        for t in self.targets:
            err = t.save()
            if err:
                return err
            
        # TODO Save all contents
        

        return None 
        
    @staticmethod
    def from_alt_path(path: Path, *args, config=Config(), conf_type=None, **kwargs):
        """
        Returns an alt instance instantiated from
        a filesystem path.
        """
        alt = Alt(name=path.stem, config=config, path=path, kwargs=kwargs)
        targets_path = Path(path, config.targets_dir_name)
        err, alt.targets = Target.from_targets_path(targets_path, alt=alt)
        
        if err:
            return err, alt
        
        #conf_type = kwargs['conf_type'] if 'conf_type' in kwargs else None
        conf_type_name = conf_type.name if conf_type else None
        
        # Make sure the targets exists
        missing_contents = []
        contents = []
        for t in alt.targets:
            content_path = Path(path, t.name)
            if not content_path.exists():
                #log('Content `{}`, declared by target `{}` is missing for type `{}` at `{}`'.format(
                #    content_path, t.target, conf_type_name, content_path
                #), warning=True)
                missing_contents.append(content_path)
            else:
                contents.append(content_path)
                
        alt.contents = contents
        alt.missing_contents = missing_contents
                
        return (None, alt)
        
# TODO: Only execute actions on call to save()
class Target:
    # Example Target('vim', Alt('vim', ...), Path(Path.home(), '.vim'))
    def __init__(self, name: str, target: Path, alt: Alt = None, config=Config(), path=None):
        self.name = name     # The name of the target (filename in .confs/alt/)
        self.alt = alt       # The alt which this is a part of
        self.target = target # The target path -> to install the file'
        self.config = config
        self.path = path     # The path to this target symlink

        self.delete = False  # Is set to true when the next call to
                             # save() should delete this target

    def __repr__(self):
        return '<Target name="{}" target="{}" path="{}" alt="{}">'.format(self.name, self.target, self.path, self.alt)
    
    def default_content_path(func):
        def wrapper(*args, **kwargs):
            if len(args) < 2 or not args[1]:
                #log('wrapped {}: {} No content_path was provided, calculating using alt'.format(func.__name__, args[0].path), warning=True)
                return func(args[0], Path(args[0].alt.path, args[0].name, **kwargs))
            else:
                func(*args, **kwargs)
        return wrapper

    def set_default_path(func):
        def wrapper(*args):
            if not args[0].path:
                args[0].path = Path(args[0].alt.path, args[0].config.targets_dir_name, args[0].name)
            return func(*args)
        return wrapper
    
    @set_default_path
    @default_content_path
    def install(self, content_path=None):
        """Creates a symlink at target pointing to the altfile 'name'"""
        if self.target.is_symlink():
            self.target.unlink()
        elif self.target.exists():
            return ExpSymlinkErr('Target dest path `{}` already exists but is not a symlink.'.format(self.target.absolute()))
        
        # NOTE: Uses absolute paths
        self.target.absolute().symlink_to(content_path.absolute())
        return None
        
    @set_default_path
    @default_content_path
    def is_installed(self, content_path=None):
        """Checks if a the target is installed."""
        #if not content_path:
        #    log('in_installed: {} No content_path was provided, calculating using alt'.format(self.path), warning=True)
        #    content_path = Path(self.alt.path, self.name)
        if not self.path:
            self.path = Path(self.alt.path, self.config.targets_dir_name, self.name)

        if self.target.is_symlink():
            # Make sure that this target is already installed.
            # This is done by checking if the target resolves to content.
            return self.target.resolve().samefile(content_path)
        return False
        
    @set_default_path
    @default_content_path
    def uninstall(self, content_path=None):
        """Removes the symlink at target IF it is installed."""
        if self.target.is_symlink():
            # Make sure that this target is already installed.
            # This is done by checking if the target resolves to content.
            if not self.target.resolve().samefile(content_path):
                return IncDataErr('Target: {} is not installed, cannot uninstall!'.format(self.path))
            self.target.unlink()
        else:
            return InvOperErr('Target `{}` is not installed!'.format(self.path))
        return None
    
    def delete(self, write_now=False):
        """Removes the target from the filesystem."""
        self.delete = True
        if write_now:
            return self.save()
        return None
    
    @set_default_path
    def save(self):
        """Saves a target"""
        if self.delete:
            if not self.path:
                self.path = Path(self.alt.path, self.config.targets_dir_name, self.name)
            if self.path.is_symlink():
                self.path.unlink()
            elif self.path.exists():
                return ExpSymlinkErr('Cannot delete target. Path `{}` is not a symlink.'.format(self.path))
            else:
                # Nothing to delete
                pass
            verbose('Deleted target: {} at {}'.format(self.name, self.path))
            return
        else:
            if self.path.is_symlink():
                self.path.unlink()
            elif self.path.exists():
                return ExpSymlinkErr('Target path `{}` is not a symlink!'.format(self.path))
            self.path.symlink_to(self.target) # !! NOTE: target does not have to exist
        return None
        
    @staticmethod
    def from_targets_path(path: Path, alt=None):
        """Returns a list of targets instance from a filesystem path."""
        if not path.is_dir():
            return (ExpDirErr('Targets-path `{}` has to be a directory!'.format(path)), None)
        targets = []

        for e in path.iterdir():
            err, target = Target.from_target_path(e, alt=alt)
            if err: return (err, None)
            targets.append(target)
        return None, targets

    @staticmethod
    def from_target_path(path: Path, alt=None):
        """Returns a target instance from a filesystem path"""
        if not path.stem:
            return (InvTargetPathErr('Target-file `{}` is invalid! A filename cannot end in \'/\'!'.format(path)), None)
        if not path.is_symlink():
            return (ExpSymlinkErr('Target-file `{}` has to be a symlink!'.format(path)), None)
        #return None, Target(name=path.stem, target=path.resolve(), alt=alt, path=path)
        target_path = Path(os.readlink(path.absolute())).absolute()
        target = Target(name=path.stem, target=target_path, alt=alt, path=path)
        return None, target
