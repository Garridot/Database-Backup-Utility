import argparse
from controllers.sqlite import SQLiteBackupUtility

def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="SQLite Database Backup Utility")
    parser.add_argument("--db-path", required=True, help="Path to the SQLite database file")
    parser.add_argument("--output-dir", required=True, help="Directory to store the backup file")
    

    # Parse the arguments
    args = parser.parse_args()

    # Controller
    controller = SQLiteBackupUtility(args.db_path, args.output_dir)
    try:
        controller.backup()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
