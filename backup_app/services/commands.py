from .config_manager import ConfigManager
from .backup_engine import BackupEngine
from typing import Callable

config = ConfigManager()
backup = BackupEngine()

class Commands:
    get_sources: Callable
    get_backup: Callable
    get_default: Callable
    add_source: Callable
    change_default: Callable
    change_backup: Callable
    rem_source: Callable
    run_backup: Callable

class CommandRegistry:
    def __init__(self, mapping: dict):
        self._mapping = {}
        
        for name, func in mapping.items():
            attr_name = name.replace("-", "_") # allow CLI-style keys
            setattr(self, attr_name, func)
            self._mapping[name] = func
    
    def __getitem__(self, key):
        return self._mapping[key]
    
    def keys(self):
        return self._mapping.keys()
    
    def items(self):
        return self._mapping.items()

class FunctionRegistry:
    def __init__(self, functions: dict):
        for name, func in functions.items():
            setattr(self, name, func)



commands: Commands = CommandRegistry(
    {
        'get-sources': config.get_sources,
        'get-backup': config.get_backup_path,
        'get-default': config.get_default_path,
        'add-source': config.add_source,
        'change-default': config.cli_default_backup,
        'change-backup': config.change_backup,
        'rem-source': config.remove_source,
        'run-backup': backup.cli_backup
    }
)
