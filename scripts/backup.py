#!/usr/bin/env python3
import boto3
import os
import schedule
import time
from datetime import datetime
import subprocess
import logging

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

def create_database_backup():
    """Create a backup of the database"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'/tmp/aksjeradar_backup_{timestamp}.sql'
        
        # Kjør database backup
        subprocess.run(['sqlite3', 'aksjeradar.db', '.dump'], 
                      stdout=open(backup_file, 'w'),
                      check=True)
        
        return backup_file
    except Exception as e:
        logger.error(f"Failed to create database backup: {str(e)}")
        return None

def upload_to_s3(file_path):
    """Upload backup to S3"""
    try:
        s3 = boto3.client('s3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        bucket_name = os.environ.get('S3_BACKUP_BUCKET')
        file_name = os.path.basename(file_path)
        
        s3.upload_file(file_path, bucket_name, f'backups/{file_name}')
        logger.info(f"Successfully uploaded {file_name} to S3")
        
        # Slett lokal backup fil
        os.remove(file_path)
        
        return True
    except Exception as e:
        logger.error(f"Failed to upload backup to S3: {str(e)}")
        return False

def backup_job():
    """Run the complete backup job"""
    logger.info("Starting backup job")
    
    backup_file = create_database_backup()
    if backup_file:
        if upload_to_s3(backup_file):
            logger.info("Backup job completed successfully")
        else:
            logger.error("Failed to upload backup to S3")
    else:
        logger.error("Failed to create backup")

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
