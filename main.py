import argparse
from db_connectors.mysql_connector import MySQLConnector
from db_connectors.sqlite_connector import SQLiteConnector
from backup_services.full_backup import FullBackup
from backup_services.sqlite_backup import SQLiteBackup
from storage.local_storage import LocalStorage
from utils.compression import compress_file
from logging.logger import setup_logger, log_info, log_error

def main():
    parser = argparse.ArgumentParser(description="Database Backup Utility")
    parser.add_argument("--db-type", required=True, help="Type of database (e.g., mysql, sqlite)")
    parser.add_argument("--host", help="Database host (required for MySQL, PostgreSQL, Mongodb)")
    parser.add_argument("--port", help="Database port (required for MySQL, PostgreSQL, Mongodb)")
    parser.add_argument("--user", help="Database user (required for MySQL, PostgreSQL, Mongodb)")
    parser.add_argument("--password", help="Database password (required for MySQL, PostgreSQL, Mongodb)")
    parser.add_argument("--database", help="Database name (required for MySQL, PostgreSQL, Mongodb)")
    parser.add_argument("--db-path", help="Path to SQLite database file (required for SQLite)")
    parser.add_argument("--output-dir", required=True, help="Output directory for backups")
    parser.add_argument("--log-file", required=True, help="Log file path")

    args = parser.parse_args()

    setup_logger(args.log_file)

    if args.db_type == "mysql":
        connector = MySQLConnector(args.host, args.port, args.user, args.password, args.database)
        if connector.connect():
            log_info("Connected to MySQL database")
            backup = FullBackup(args.db_type, args.database, args.output_dir)
            backup_file = backup.backup()
            log_info(f"Backup completed: {backup_file}")

            compressed_file = f"{backup_file}.gz"
            compress_file(backup_file, compressed_file)
            log_info(f"Backup compressed: {compressed_file}")

            storage = LocalStorage(args.output_dir)
            storage.save(compressed_file)
            log_info(f"Backup saved to local storage: {args.output_dir}")

            connector.disconnect()
            log_info("Disconnected from MySQL database")
        else:
            log_error("Failed to connect to MySQL database")

    elif args.db_type == "sqlite":
        if not args.db_path:
            log_error("SQLite database path (--db-path) is required")
            return

        connector = SQLiteConnector(args.db_path)
        if connector.connect():
            log_info("Connected to SQLite database")
            backup = SQLiteBackup(args.db_path, args.output_dir)
            backup_file = backup.backup()
            log_info(f"Backup completed: {backup_file}")

            compressed_file = f"{backup_file}.gz"
            compress_file(backup_file, compressed_file)
            log_info(f"Backup compressed: {compressed_file}")

            storage = LocalStorage(args.output_dir)
            storage.save(compressed_file)
            log_info(f"Backup saved to local storage: {args.output_dir}")

            connector.disconnect()
            log_info("Disconnected from SQLite database")
        else:
            log_error("Failed to connect to SQLite database")

if __name__ == "__main__":
    main()