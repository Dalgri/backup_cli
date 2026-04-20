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
        

class SetupDefaults:
    def __init__(self):
        self.filemanager = FileManager()
        
    def get_defaults(self):
        if self.filemanager._conf is None:
            self.filemanager.load()
            
            default = Path.home() / 'Documents' / 'backup'
            if not default.exists():
                default.mkdir(parents=True, exist_ok=True)
            conf = self.filemanager._conf
            conf.setdefault('source', [])
            conf.setdefault('default_backup', str(default))
            conf.setdefault('backup', str(self.conf['default_backup']))
            self.filemanager.save(conf)

class Executables:
    def __init__(self):
        self.filemanager = FileManager()
    
    def conf(self):
        return self.filemanager.load()
        
    def cli_default_backup(self, add):
        if not add:
            return
        conf = self.conf()
        conf['default_backup'] = str(Path(add).resolve())
        self.filemanager.save(conf)
        print(f'Successfully swapped default_backup to {add}')
    
    
    def change_backup(self, path):
        if not path:
            return
        conf = self.conf()
        conf['backup'] = str(Path(path).resolve())
        self.filemanager.save(conf)
        print(f'Successfully swapped backup to {path}') 

    def remove_source(self, idx):
        conf = self.conf()
        removed = conf["source"].pop(idx)
        self.filemanager.save(conf)
        return removed
    
    def add_source(self, path: str):
        conf = self.conf()
        sources = conf.setdefault('source', [])
        sources.append(str(Path(path).resolve()))
        self.filemanager.save(conf)
        
    def get_sources(self):
        return self.conf().get('source', [])
    
    def get_backup_path(self):
        return self.conf().get('backup', 'Not set')
    
    def get_default_path(self):
        return self.conf().get('default_backup', 'not set')