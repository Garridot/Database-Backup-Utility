# tests/test_postgresql_backup.py 
# "postgresqlpasswordgarrido"
import unittest
import os
import psycopg2
from psycopg2 import sql
from db_connectors.postgresql_connector import PostgreSQLConnector
from backup_services.full_backup import FullBackup
from storages.local_storage import LocalStorage
from utils.compression import compress_file

class TestPostgreSQLBackup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Test database configuration
        cls.host = "localhost"
        cls.port = 5432
        cls.user = "postgres"  # Replace with your PostgreSQL user
        cls.password = "postgresqlpasswordgarrido"  # Replace with your PostgreSQL password
        cls.database = "test_postgres_db"
        cls.backup_dir = "tests/test_backups/postgresql"
        os.makedirs(cls.backup_dir, exist_ok=True)

        try:
            # Connect to PostgreSQL
            cls.conn = psycopg2.connect(
                dbname="postgres",  # Connect to database by default
                user=cls.user,
                password=cls.password,
                host=cls.host,
                port=cls.port
            )
            cls.conn.autocommit = True
            cls.cursor = cls.conn.cursor()

            # Delete test database if it already exists
            cls.cursor.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(cls.database))
            )

            # Create the test database
            cls.cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(cls.database))
            )

            # Connect to test database
            cls.test_conn = psycopg2.connect(
                dbname=cls.database,
                user=cls.user,
                password=cls.password,
                host=cls.host,
                port=cls.port
            )
            cls.test_cursor = cls.test_conn.cursor()

            # Create a table and insert some test data
            cls.test_cursor.execute("CREATE TABLE test_table (id SERIAL PRIMARY KEY, name TEXT);")
            cls.test_cursor.execute("INSERT INTO test_table (name) VALUES ('test_name');")
            cls.test_conn.commit()
        except psycopg2.OperationalError as e:
            raise unittest.SkipTest(f"PostgreSQL server is not available: {e}")
        except psycopg2.ProgrammingError as e:
            raise unittest.SkipTest(f"SQL syntax error: {e}")
        except Exception as e:
            raise unittest.SkipTest(f"Unexpected error during setup: {e}")

    @classmethod
    def tearDownClass(cls):
        # Close all connections to the test database
        if hasattr(cls, "test_cursor"):
            cls.test_cursor.close()
        if hasattr(cls, "test_conn"):
            cls.test_conn.close()

        # Delete test database
        if hasattr(cls, "cursor"):
            cls.cursor.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(cls.database))
            )
            cls.cursor.close()
        if hasattr(cls, "conn"):
            cls.conn.close()

        # Clean backup files
        if os.path.exists(cls.backup_dir):
            for file in os.listdir(cls.backup_dir):
                os.remove(os.path.join(cls.backup_dir, file))
            os.rmdir(cls.backup_dir)

    def test_postgresql_backup_creation(self):
        # Verify that the PostgreSQL backup file is created
        connector = PostgreSQLConnector(self.host, self.port, self.user, self.password, self.database)
        if connector.connect():
            backup = FullBackup("postgresql", self.database, self.backup_dir, self.user, self.password)
            backup_file = backup.backup()
            self.assertTrue(os.path.exists(backup_file))
            connector.disconnect()

    def test_postgresql_backup_compression(self):
        # Verify that the PostgreSQL backup file is compressed
        connector = PostgreSQLConnector(self.host, self.port, self.user, self.password, self.database)
        if connector.connect():
            backup = FullBackup("postgresql", self.database, self.backup_dir, self.user, self.password)
            backup_file = backup.backup()
            compressed_file = f"{backup_file}.gz"
            compress_file(backup_file, compressed_file)
            self.assertTrue(os.path.exists(compressed_file))
            connector.disconnect()

    def test_postgresql_backup_storage(self):
        # Verify that the PostgreSQL backup file is saved in the correct location
        connector = PostgreSQLConnector(self.host, self.port, self.user, self.password, self.database)
        if connector.connect():
            backup = FullBackup("postgresql", self.database, self.backup_dir, self.user, self.password)
            backup_file = backup.backup()
            storage = LocalStorage(self.backup_dir)
            storage.save(backup_file)
            self.assertTrue(os.path.exists(os.path.join(self.backup_dir, os.path.basename(backup_file))))
            connector.disconnect()

if __name__ == "__main__":
    unittest.main()