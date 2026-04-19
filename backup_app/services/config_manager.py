import json
from pathlib import Path
from json_repair import repair_json

class ConfigManager():
    
    def __init__(self, path='conf_file.json'):
        self.conf_file = Path(path)
        self.conf = self.load_conf()
        self.get_defaults()
    
    def load_conf(self):
        if not self.conf_file.exists():
            return {}
        
        try:
            
            with open(self.conf_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # read broken json as string
            with open(self.conf_file, 'r', encoding='utf-8') as f:
                broken = f.read()
            
            # repair it
            fixed = repair_json(broken)
            
            # Load repaired json
            data = json.loads(fixed)
            
            # overwrite file with fixed version
            with open(self.conf_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4) 
            return data
                
    def save_data(self):
        with open(self.conf_file, 'w') as f:
            json.dump(self.conf, f, indent=2)
            
    def cli_default_backup(self, add):
        if not add:
            return
        self.conf['default_backup'] = str(Path(add).resolve())
        self.save_data()
        print(f'Successfully swapped default_backup to {add}')
    
    def get_defaults(self):
        if not self.conf_file.exists():
            
            default = Path.home() / 'Documents' / 'backup'
            if not default.exists():
                default.mkdir(parents=True, exist_ok=True)
            
            self.conf.setdefault('source', [])
            self.conf.setdefault('default_backup', str(default))
            self.conf.setdefault('backup', str(self.conf['default_backup']))
            self.save_data()
    
    def change_backup(self, path):
        if not path:
            return
        self.conf['backup'] = str(Path(path).resolve())
        self.save_data()
        print(f'Successfully swapped backup to {path}') 

    def remove_source(self, idx):
        removed = self.conf["source"].pop(idx)
        self.save_data()
        return removed
    
    def add_source(self, path: str):
        self.conf.setdefault('source', []).append(str(Path(path).resolve()))
        self.save_data()
        
    def get_sources(self):
        return self.conf.get('source', [])
    
    def get_backup_path(self):
        return self.conf.get('backup', 'Not set')
    
    def get_default_path(self):
        return self.conf.get('default_backup', 'not set')
    
