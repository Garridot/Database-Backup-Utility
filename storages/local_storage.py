import os

class LocalStorage:
    def __init__(self, backup_dir):
        self.backup_dir = backup_dir

    def save(self, backup_file):
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        os.rename(backup_file, os.path.join(self.backup_dir, os.path.basename(backup_file)))