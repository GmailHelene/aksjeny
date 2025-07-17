#!/usr/bin/env python3
"""
Management CLI for Aksjeradar - Performance and system management
"""
import click
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import text

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.performance_monitor import PerformanceMonitor
from flask import Flask
from config import config

def create_app():
    """Create minimal Flask app for CLI commands"""
    app = Flask(__name__)
    app.config.from_object(config['default'])
    return app

@click.group()
def cli():
    """Aksjeradar Management CLI"""
    pass

@cli.command()
@click.option('--hours', default=24, help='Number of hours to analyze (default: 24)')
def performance(hours):
    """Show performance statistics"""
    app = create_app()
    with app.app_context():
        monitor = PerformanceMonitor()
        
        print(f"\n🚀 Aksjeradar Performance Report - Last {hours} hours")
        print("=" * 60)
        
        try:
            stats = monitor.get_performance_stats(hours=hours)
            
            print(f"📊 Overview:")
            print(f"  • Total requests: {stats.get('total_requests', 0)}")
            print(f"  • Average response time: {stats.get('avg_response_time', 0):.2f}ms")
            print(f"  • Error count: {stats.get('error_count', 0)}")
            print(f"  • Error rate: {stats.get('error_rate', 0):.2f}%")
            
            print(f"\n🐌 Slowest endpoints:")
            for endpoint in stats.get('slowest_endpoints', [])[:5]:
                print(f"  • {endpoint['endpoint']}: {endpoint['avg_time']:.2f}ms ({endpoint['count']} reqs)")
            
            print(f"\n📈 Most used endpoints:")
            for endpoint in stats.get('most_used_endpoints', [])[:5]:
                print(f"  • {endpoint['endpoint']}: {endpoint['count']} requests ({endpoint['avg_time']:.2f}ms avg)")
            
            print(f"\n⚠️  Recent errors:")
            error_log = monitor.get_error_log(limit=10)
            if error_log:
                for error in error_log[:5]:
                    print(f"  • {error['timestamp']} - {error['endpoint']}: {error['error_message'][:50]}...")
            else:
                print("  • No errors found! 🎉")
                
        except Exception as e:
            print(f"❌ Error getting performance stats: {e}")

@cli.command()
@click.option('--limit', default=20, help='Number of recent errors to show (default: 20)')
def errors(limit):
    """Show recent errors"""
    app = create_app()
    with app.app_context():
        monitor = PerformanceMonitor()
        
        print(f"\n🚨 Recent Errors (last {limit})")
        print("=" * 60)
        
        try:
            error_log = monitor.get_error_log(limit=limit)
            
            if not error_log:
                print("✅ No errors found!")
                return
            
            for i, error in enumerate(error_log, 1):
                print(f"\n{i}. {error['timestamp']}")
                print(f"   Endpoint: {error['endpoint']}")
                print(f"   Error: {error['error_message']}")
                print(f"   User: {error.get('user_id', 'Anonymous')}")
                
        except Exception as e:
            print(f"❌ Error getting error log: {e}")

@cli.command()
def status():
    """Show system status"""
    print("\n🔍 System Status")
    print("=" * 30)
    
    # Check if performance log exists
    monitor = PerformanceMonitor()
    if os.path.exists(monitor.log_file):
        size = os.path.getsize(monitor.log_file)
        print(f"📊 Performance log: {size} bytes")
    else:
        print("📊 Performance log: Not found")
    
    # Check if error log exists
    if os.path.exists(monitor.error_log):
        size = os.path.getsize(monitor.error_log)
        print(f"🚨 Error log: {size} bytes")
    else:
        print("🚨 Error log: Not found")
    
    # Check database connection
    try:
        app = create_app()
        with app.app_context():
            from app.extensions import db
            db.session.execute(text('SELECT 1'))
            print("✅ Database: Connected")
    except Exception as e:
        print(f"❌ Database: Error - {e}")

if __name__ == '__main__':
    cli()
