import json
from pathlib import Path
from json_repair import repair_json

class FileManager:
    def __init__(self, path: str='conf_file.json'):
        self.conf_file = Path(path)
        self._conf = None
    
    def load(self):
        if not self.conf_file.exists():
            self._conf = {}
            return self._conf
        
        try:
            
            with open(self.conf_file, 'r') as f:
                self._conf = json.load(f)
            
        except json.JSONDecodeError:
            self._conf = self._repair_and_load()
        
        return self._conf
    
    def save(self, data):
        if data is None:
            data = self._conf
        
        if data is None:
            return
        
        with open(self.conf_file, 'w') as f:
            json.dump(data, f, indent=2)
        self._conf = data
        
        
    def _repair_and_load(self):
        # read broken json as string
            with open(self.conf_file, 'r', encoding='utf-8') as f:
                broken = f.read()
            
            # repair it
            fixed = repair_json(broken)
            
            # Load repaired json
            data = json.loads(fixed)
            
            # overwrite file with fixed version
            self.save(data) 
            return data 

class ConfigManager:
    
    def __init__(self, path: str = 'conf_file.json'):
        self._fm = FileManager(path)
        self._conf = None
        
    def _ensure_loaded(self):
        if self._conf is None:
            self._conf = self._fm.load()
            
    def bootstrap_defaults(self):
        # Ensure config file exists with sensible default. Call once on startup.
        self._ensure_loaded()
        
        default = Path.home() / 'Documents' / 'backup'
        default.mkdir(parents=True, exist_ok=True)
        
        self._conf.setdefault('source', [])
        self._conf.setdefault('default_backup', str(default))
        self._conf.setdefault('backup', self._conf['default_backup'])
        
        self._fm.save(self._conf)
    
    # ---- all the Executables methods live here ----
    
    def add_source(self, path: str):
        self._ensure_loaded()
        self._conf.setdefault('source', []).append(str(Path(path).resolve()))
        self._fm.save(self._conf)
        
    def remove_source(self, idx: int):
        self._ensure_loaded()
        removed = self._conf['source'].pop(idx)
        self._fm.save(self._conf)
        return removed
    
    def get_sources(self):
        self._ensure_loaded()
        return self._conf.get('source', [])
    
    def get_backup_path(self):
        self._ensure_loaded()
        return self._conf.get('backup', 'Not set')
    
    def get_default_path(self):
        self._ensure_loaded()
        return self._conf.get('default_backup', 'Not set')
    
    def cli_default_backup(self, add):
        if not add:
            return
        self._ensure_loaded()
        self._conf['default_backup'] = str(Path(add).resolve())
        self._fm.save(self._conf)
        print(f'Successfully swapped default_backup to {add}')
        
    def change_backup(self, path):
        if not path:
            return
        self._ensure_loaded()
        self._conf['backup'] = str(Path(path).resolve())
        self._fm.save(self._conf)
        print(f'Successfully swapped backup to {path}')
        
    