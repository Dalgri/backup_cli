import shutil
from pathlib import Path
from .config_manager import ConfigManager
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from backup_app.utils.logger import Logger

class BackupEngine:
    def __init__(self):
        self.config = ConfigManager()
        self.config.bootstrap_defaults()
        self.logger = Logger()
        
    def _files_differ(self, src: Path, dst: Path) -> bool:
        # Returns True if src should overwrite dst, rsync-style
        if not dst.exists():
            return True
        
        src_stat = src.stat()
        dst_stat = dst.stat()
        
        # Stage 1: size mimatch -> definatly different
        if src_stat.st_size != dst_stat.st_size:
            return True
        
        # Stage 2: mtime mismatch -> likely different
        if src_stat.st_mtime != dst_stat.st_mtime:
            # Stage 3: confirm with checksum (only reached if size matches)
            return self._checksum(src) != self._checksum(dst)
        
        return False # same size + same mtime -> assume identical
    
    def _checksum(self, path: Path, block_size: int = 65536) -> str:
        h = hashlib.md5(usedforsecurity=False)
        with open(path, 'rb') as f:
            while chunk := f.read(block_size):
                h.update(chunk)
        return h.hexdigest()
    
    def cli_backup(self, dry_run: bool = False):
        sources = self.config.get_sources()
        backup_root = Path(self.config.get_backup_path() or self.config.get_default_path())
        if not dry_run:
            
            backup_root.mkdir(parents=True, exist_ok=True)
        
        def copy_file(path, base_path):
            
            try:
                relative = path.relative_to(base_path)
                dst = backup_root / base_path.name / relative
                if not dst.exists() or self._files_differ(path, dst):
                    if dry_run:
                        self.logger.log_dry(path, dst)
                    else:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(path, dst)
                        self.logger.log_info(path, dst)
            except Exception as e:
                self.logger.log_error(path, e)
        
        tasks = [
            (path, Path(src))
            for src in sources
            if (base_path := Path(src)).exists()
            for path in base_path.rglob('*')
            if path.is_file()
        ]
        
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(copy_file, p, b): p for p, b in tasks}
            for future in as_completed(futures):
                future.result() # surfaces exceptions if needed
        if dry_run:
            
            print('Dry run complete - no files were copied.')
        else:
            
            print('Backup successfully completed!')
        