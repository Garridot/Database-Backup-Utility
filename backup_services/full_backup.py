import subprocess
import os
from datetime import datetime

class FullBackup:
    def __init__(self, db_type, db_name, output_dir, db_user, db_password):
        """
        Initialize the FullBackup class.

        :param db_type: Type of database (e.g., "mysql").
        :param db_name: Name of the database to back up.
        :param output_dir: Directory to save the backup file.
        :param db_user: Database username.
        :param db_password: Database password.
        """
        self.db_type = db_type
        self.db_name = db_name
        self.output_dir = output_dir
        self.db_user = db_user
        self.db_password = db_password

    def backup(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file = os.path.join(self.output_dir, f"{self.db_name}_full_{timestamp}.sql")
        
        if self.db_type == "mysql":
            # Use mysqldump to create a backup
            command = f"mysqldump --user={self.db_user} --password={self.db_password} {self.db_name} > {backup_file}"
        elif self.db_type == "postgresql":
            # Use pg_dump to create a backup for PostgreSQL
            command = f"pg_dump --host=localhost --username={self.db_user} --password={self.db_password} --dbname={self.db_name} --file={backup_file}"

        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to execute: {e}")
        return backup_file