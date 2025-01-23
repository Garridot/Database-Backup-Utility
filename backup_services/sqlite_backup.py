import shutil
import os
from datetime import datetime

class SQLiteBackup:
    def __init__(self, db_path, output_dir):
        self.db_path = db_path
        self.output_dir = output_dir

    def backup(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file = os.path.join(self.output_dir, f"{os.path.basename(self.db_path)}_backup_{timestamp}.db")
        
        # Copy the SQLite database file to the backup location
        shutil.copy2(self.db_path, backup_file)
        return backup_file