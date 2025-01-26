# tests/test_mysql_backup.py
import unittest
import os
import pymysql
from db_connectors.mysql_connector import MySQLConnector
from backup_services.full_backup import FullBackup
from storages.local_storage import LocalStorage
from utils.compression import compress_file


class TestMySQLBackup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up MySQL test database
        cls.host = "localhost"
        cls.port = 3306
        cls.user = "root"  # Replace with your MySQL username
        cls.password = "yourpassword"  # Replace with your MySQL password
        cls.database = "test_mysql_db"
        cls.backup_dir = "tests/test_backups/mysql"
        os.makedirs(cls.backup_dir, exist_ok=True)

        try:
            # Connect to MySQL
            cls.conn = pymysql.connect(
                host=cls.host,
                port=cls.port,
                user=cls.user,
                password=cls.password
            )
            cls.cursor = cls.conn.cursor()

            # Create the test database if it doesn't exist
            create_db_query = f"CREATE DATABASE IF NOT EXISTS `{cls.database}`;"
            print(f"Executing query: {create_db_query}")  # Debugging
            cls.cursor.execute(create_db_query)

            # Switch to the test database
            use_db_query = f"USE `{cls.database}`;"
            print(f"Executing query: {use_db_query}")  # Debugging
            cls.cursor.execute(use_db_query)

            # Create a test table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS test_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255)
            );
            """
            print(f"Executing query: {create_table_query}")  # Debugging
            cls.cursor.execute(create_table_query)

            # Insert test data
            insert_data_query = "INSERT INTO test_table (name) VALUES ('test_name');"
            print(f"Executing query: {insert_data_query}")  # Debugging
            cls.cursor.execute(insert_data_query)

            cls.conn.commit()
        except pymysql.err.OperationalError as e:
            raise unittest.SkipTest(f"MySQL server is not available: {e}")
        except pymysql.err.ProgrammingError as e:
            raise unittest.SkipTest(f"SQL syntax error: {e}")

    @classmethod
    def tearDownClass(cls):
        # Clean up MySQL test database and backups
        if hasattr(cls, "conn"):
            drop_db_query = f"DROP DATABASE IF EXISTS `{cls.database}`;"
            print(f"Executing query: {drop_db_query}")  # Debugging
            cls.cursor.execute(drop_db_query)
            cls.conn.close()
        if os.path.exists(cls.backup_dir):
            for file in os.listdir(cls.backup_dir):
                os.remove(os.path.join(cls.backup_dir, file))
            os.rmdir(cls.backup_dir)

    def test_mysql_backup_creation(self):
        # Test if the MySQL backup file is created
        connector = MySQLConnector(self.host, self.port, self.user, self.password, self.database)
        if connector.connect():
            backup = FullBackup("mysql", self.database, self.backup_dir, self.user, self.password)
            backup_file = backup.backup()
            self.assertTrue(os.path.exists(backup_file))
            connector.disconnect()

    def test_mysql_backup_compression(self):
        # Test if the MySQL backup file is compressed
        connector = MySQLConnector(self.host, self.port, self.user, self.password, self.database)
        if connector.connect():
            backup = FullBackup("mysql", self.database, self.backup_dir, self.user, self.password)
            backup_file = backup.backup()
            compressed_file = f"{backup_file}.gz"
            compress_file(backup_file, compressed_file)
            self.assertTrue(os.path.exists(compressed_file))
            connector.disconnect()

    def test_mysql_backup_storage(self):
        # Test if the MySQL backup file is saved to the correct location
        connector = MySQLConnector(self.host, self.port, self.user, self.password, self.database)
        if connector.connect():
            backup = FullBackup("mysql", self.database, self.backup_dir, self.user, self.password)
            backup_file = backup.backup()
            storage = LocalStorage(self.backup_dir)
            storage.save(backup_file)
            self.assertTrue(os.path.exists(os.path.join(self.backup_dir, os.path.basename(backup_file))))
            connector.disconnect()

if __name__ == "__main__":
    unittest.main()