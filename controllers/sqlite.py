import os
import sqlite3
import gzip
import shutil
from datetime import datetime

class SQLiteBackupUtility:
    """
    Utility class for backing up SQLite databases with compression and local storage.
    """

    def __init__(self, db_path, backup_dir):
        self.db_path = db_path
        self.backup_dir = backup_dir

    def _validate_paths(self):
        """Validates the database path and ensures the backup directory exists."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def _generate_backup_filename(self):
        """Generates a timestamped filename for the backup file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(self.backup_dir, f"backup_{timestamp}.db.gz")

    def _compress_backup(self, source, destination):
        """Compresses the backup file using gzip."""
        with open(source, 'rb') as src_file:
            with gzip.open(destination, 'wb') as gz_file:
                shutil.copyfileobj(src_file, gz_file)

    def backup(self):
        """
        Performs the backup operation:
        - Copies the database file.
        - Compresses the backup.
        - Saves the compressed file to the backup directory.
        """
        try:
            self._validate_paths()

            # Create a temporary backup file
            temp_backup_path = self._generate_backup_filename().replace('.gz', '')
            shutil.copy2(self.db_path, temp_backup_path)

            # Compress the backup file
            compressed_backup_path = temp_backup_path + ".gz"
            self._compress_backup(temp_backup_path, compressed_backup_path)

            # Remove the uncompressed temporary backup file
            os.remove(temp_backup_path)

            print(f"Backup completed successfully: {compressed_backup_path}")
            return compressed_backup_path

        except Exception as e:
            print(f"Backup failed: {e}")
            raise