#!/usr/bin/env python3
import os
import shutil
from datetime import datetime
import logging
import schedule
import time

# Sett opp logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/aksjeradar/backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('backup')

# Konfigurer backup-mappe
BACKUP_DIR = os.environ.get('BACKUP_DIR', 'backups')
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def create_database_backup():
    """Create a backup of the database"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'{BACKUP_DIR}/aksjeradar_backup_{timestamp}.sql'
        
        # Kjør database backup
        os.system(f'sqlite3 aksjeradar.db ".backup {backup_file}"')
        
        # Behold bare de 5 siste backupene
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.sql')])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))
        
        logger.info(f"Backup created successfully: {backup_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        return False

def backup_job():
    """Run the backup job"""
    logger.info("Starting backup job")
    if create_database_backup():
        logger.info("Backup job completed successfully")
    else:
        logger.error("Backup job failed")

def main():
    """Main function to run scheduled backups"""
    # Kjør backup hver dag kl 03:00
    schedule.every().day.at("03:00").do(backup_job)
    
    # Kjør backup når scriptet starter
    backup_job()
    
    # Hold scriptet kjørende
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
