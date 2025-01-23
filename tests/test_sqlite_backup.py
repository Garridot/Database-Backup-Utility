# tests/test_sqlite_backup.py
import unittest
import os
import sqlite3
from db_connectors.sqlite_connector import SQLiteConnector
from backup_services.sqlite_backup import SQLiteBackup
from storages.local_storage import LocalStorage
from utils.compression import compress_file

class TestSQLiteBackup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test SQLite database
        cls.test_db_path = "tests/test_data/test_sqlite.db"
        cls.conn = sqlite3.connect(cls.test_db_path)
        cls.cursor = cls.conn.cursor()
        cls.cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
        cls.cursor.execute("INSERT INTO test_table (name) VALUES ('test_name')")
        cls.conn.commit()

        # Set up backup directory
        cls.backup_dir = "tests/test_backups/sqlite"
        os.makedirs(cls.backup_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # Clean up test database and backups
        cls.conn.close()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        for file in os.listdir(cls.backup_dir):
            os.remove(os.path.join(cls.backup_dir, file))
        os.rmdir(cls.backup_dir)

    def test_sqlite_backup_creation(self):
        # Test if the backup file is created
        backup = SQLiteBackup(self.test_db_path, self.backup_dir)
        backup_file = backup.backup()
        self.assertTrue(os.path.exists(backup_file))

    def test_sqlite_backup_compression(self):
        # Test if the backup file is compressed
        backup = SQLiteBackup(self.test_db_path, self.backup_dir)
        backup_file = backup.backup()
        compressed_file = f"{backup_file}.gz"
        compress_file(backup_file, compressed_file)
        self.assertTrue(os.path.exists(compressed_file))

    def test_sqlite_backup_storage(self):
        # Test if the backup file is saved to the correct location
        backup = SQLiteBackup(self.test_db_path, self.backup_dir)
        backup_file = backup.backup()
        storage = LocalStorage(self.backup_dir)
        storage.save(backup_file)
        self.assertTrue(os.path.exists(os.path.join(self.backup_dir, os.path.basename(backup_file))))

if __name__ == "__main__":
    unittest.main()