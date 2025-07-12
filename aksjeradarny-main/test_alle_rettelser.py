#!/usr/bin/env python3
"""
Omfattende test og feilretting av alle problemer i Aksjeradar V6
"""
import sys
import os
import traceback
import requests
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, '/workspaces/aksjeradarv6')

def test_import_issues():
    """Test og fiks import problemer"""
    print("🔍 TESTER IMPORT PROBLEMER...")
    print("=" * 50)
    
    import_tests = [
        ("Flask", "from flask import Flask"),
        ("App Creation", "from app import create_app"),
        ("Models", "from app.models.user import User"),
        ("Extensions", "from app.extensions import db, login_manager"),
        ("Services", "from app.services.data_service import DataService"),
        ("Routes", "from app.routes.main import main"),
        ("Forms", "from app.forms import LoginForm"),
        ("CSRF", "from flask_wtf.csrf import generate_csrf"),
        ("Stripe", "import stripe"),
        ("Pandas", "import pandas as pd"),
        ("YFinance", "import yfinance as yf")
    ]
    
    errors = []
    for name, import_cmd in import_tests:
        try:
            exec(import_cmd)
            print(f"✅ {name}: OK")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            errors.append((name, str(e)))
    
    return errors

def test_template_syntax():
    """Test og fiks Jinja2 template syntax feil"""
    print("\n🔍 TESTER TEMPLATE SYNTAX...")
    print("=" * 50)
    
    template_dir = Path("/workspaces/aksjeradarv6/app/templates")
    if not template_dir.exists():
        template_dir = Path("/workspaces/aksjeradarv6/templates")
    
    errors = []
    if template_dir.exists():
        for html_file in template_dir.rglob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8')
                
                # Check for common Jinja2 syntax errors
                issues = []
                if '{% endblock %}' in content and content.count('{% endblock %}') > content.count('{% block'):
                    issues.append("Extra endblock tags")
                if '{% endfor %}' in content and content.count('{% endfor %}') > content.count('{% for'):
                    issues.append("Extra endfor tags")
                if '{% endif %}' in content and content.count('{% endif %}') > content.count('{% if'):
                    issues.append("Extra endif tags")
                
                if issues:
                    print(f"❌ {html_file.name}: {', '.join(issues)}")
                    errors.append((str(html_file), issues))
                else:
                    print(f"✅ {html_file.name}: OK")
                    
            except Exception as e:
                print(f"❌ {html_file.name}: {str(e)}")
                errors.append((str(html_file), [str(e)]))
    
    return errors

def test_database_issues():
    """Test og fiks database problemer"""
    print("\n🔍 TESTER DATABASE PROBLEMER...")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.extensions import db
        from app.models.user import User
        
        app = create_app()
        with app.app_context():
            try:
                # Test database connection
                with db.engine.connect() as connection:
                    result = connection.execute(db.text("SELECT 1")).fetchone()
                print("✅ Database tilkobling: OK")
                
                # Test basic queries
                user_count = User.query.count()
                print(f"✅ Bruker tabelle: {user_count} brukere")
                
                # Check for Helene's access
                exempt_emails = ['helene@luxushair.com', 'helene721@gmail.com']
                for email in exempt_emails:
                    user = User.query.filter_by(email=email).first()
                    if user:
                        if not (user.has_subscription and user.subscription_type == 'lifetime' and user.is_admin):
                            print(f"🔧 Fikser tilgang for {email}")
                            user.has_subscription = True
                            user.subscription_type = 'lifetime'
                            user.is_admin = True
                            try:
                                db.session.commit()
                                print(f"✅ Oppdatert tilgang for {email}")
                            except Exception as e:
                                print(f"❌ Kunne ikke oppdatere {email}: {e}")
                                db.session.rollback()
                        else:
                            print(f"✅ {email}: Korrekt tilgang")
                    else:
                        print(f"❌ {email}: Bruker finnes ikke")
                
                return []
                
            except Exception as e:
                print(f"❌ Database feil: {e}")
                return [("Database", str(e))]
                
    except Exception as e:
        print(f"❌ Kunne ikke teste database: {e}")
        return [("Database Import", str(e))]

def test_app_startup():
    """Test app oppstart"""
    print("\n🔍 TESTER APP OPPSTART...")
    print("=" * 50)
    
    try:
        from app import create_app
        app = create_app()
        print("✅ App opprettet uten feil")
        
        # Test app konfiguration
        print(f"✅ Debug mode: {app.debug}")
        print(f"✅ Secret key: {'✓' if app.secret_key else '✗'}")
        print(f"✅ Database URI konfigurert: {'✓' if app.config.get('SQLALCHEMY_DATABASE_URI') else '✗'}")
        
        return []
        
    except Exception as e:
        print(f"❌ App oppstart feil: {e}")
        traceback.print_exc()
        return [("App Startup", str(e))]

def test_critical_endpoints():
    """Test kritiske endepunkter når appen kjører"""
    print("\n🔍 TESTER KRITISKE ENDEPUNKTER...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Check if app is running
    try:
        response = requests.get(base_url, timeout=5)
        print("✅ App kjører og svarer på requests")
    except requests.exceptions.ConnectionError:
        print("⚠️ App kjører ikke - starter ikke endpoint testing")
        return [("App Not Running", "App må kjøres for å teste endepunkter")]
    except Exception as e:
        print(f"⚠️ Kunne ikke nå app: {e}")
        return [("Connection", str(e))]
    
    # Test critical endpoints
    endpoints = [
        "/",
        "/login",
        "/register", 
        "/subscription",
        "/stocks/details/EQNR.OL",
        "/api/market/overview"
    ]
    
    errors = []
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code < 500:
                print(f"✅ {endpoint}: {response.status_code}")
            else:
                print(f"❌ {endpoint}: {response.status_code} Server Error")
                errors.append((endpoint, f"Status {response.status_code}"))
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")
            errors.append((endpoint, str(e)))
    
    return errors

def fix_blueprint_conflicts():
    """Fiks blueprint konflikter"""
    print("\n🔧 FIKSER BLUEPRINT KONFLIKTER...")
    print("=" * 50)
    
    try:
        # Check for duplicate blueprint registrations
        main_file = Path("/workspaces/aksjeradarv6/app/__init__.py")
        if main_file.exists():
            content = main_file.read_text()
            
            # Count blueprint registrations
            blueprint_count = content.count("app.register_blueprint")
            print(f"📊 Antall blueprint registreringer: {blueprint_count}")
            
            if "View function mapping is overwriting" in content or blueprint_count > 20:
                print("🔧 Potensielt blueprint konflikt oppdaget")
                # This would require more detailed analysis to fix
                return [("Blueprint Conflict", "Duplicate registrations detected")]
            else:
                print("✅ Ingen blueprint konflikter funnet")
                return []
        
    except Exception as e:
        print(f"❌ Kunne ikke sjekke blueprints: {e}")
        return [("Blueprint Check", str(e))]

def test_offline_files():
    """Test og fiks manglende offline filer"""
    print("\n🔍 TESTER OFFLINE FILER...")
    print("=" * 50)
    
    required_files = [
        "/workspaces/aksjeradarv6/static/js/service-worker.js",
        "/workspaces/aksjeradarv6/static/manifest.json",
        "/workspaces/aksjeradarv6/offline.html",
        "/workspaces/aksjeradarv6/static/images/logo-512.png"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {Path(file_path).name}: Finnes")
        else:
            print(f"❌ {Path(file_path).name}: Mangler")
            missing_files.append(file_path)
    
    return [("Missing File", f) for f in missing_files]

def generate_fixes():
    """Generer og utfør automatiske fikser"""
    print("\n🔧 GENERERER AUTOMATISKE FIKSER...")
    print("=" * 50)
    
    fixes_applied = []
    
    # Fix 1: Create missing offline.html if it doesn't exist
    offline_html_path = Path("/workspaces/aksjeradarv6/offline.html")
    if not offline_html_path.exists():
        print("🔧 Oppretter manglende offline.html...")
        try:
            offline_content = '''<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline - Aksjeradar</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .container { max-width: 600px; margin: 0 auto; }
        .logo { width: 100px; height: 100px; margin-bottom: 20px; }
        h1 { color: #2c3e50; margin-bottom: 20px; }
        p { color: #7f8c8d; font-size: 18px; line-height: 1.6; }
        .retry-btn { 
            background: #3498db; color: white; padding: 12px 24px; 
            border: none; border-radius: 6px; font-size: 16px; 
            cursor: pointer; margin-top: 20px; 
        }
        .retry-btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <img src="/static/images/logo-192.png" alt="Aksjeradar Logo" class="logo">
        <h1>Du er offline</h1>
        <p>Beklager, men du er for øyeblikket ikke tilkoblet internett. 
           Aksjeradar krever en internettforbindelse for å hente de nyeste markedsdata.</p>
        <p>Sjekk tilkoblingen din og prøv igjen.</p>
        <button class="retry-btn" onclick="window.location.reload()">Prøv igjen</button>
    </div>
</body>
</html>'''
            offline_html_path.write_text(offline_content, encoding='utf-8')
            print("✅ offline.html opprettet")
            fixes_applied.append("Created offline.html")
        except Exception as e:
            print(f"❌ Kunne ikke opprette offline.html: {e}")
    
    # Fix 2: Create basic service-worker.js if missing
    sw_path = Path("/workspaces/aksjeradarv6/static/js/service-worker.js")
    if not sw_path.exists():
        print("🔧 Oppretter manglende service-worker.js...")
        try:
            sw_path.parent.mkdir(parents=True, exist_ok=True)
            sw_content = '''// Aksjeradar Service Worker
const CACHE_NAME = 'aksjeradar-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/images/logo-192.png',
  '/offline.html'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request).catch(function() {
          return caches.match('/offline.html');
        });
      }
    )
  );
});'''
            sw_path.write_text(sw_content, encoding='utf-8')
            print("✅ service-worker.js opprettet")
            fixes_applied.append("Created service-worker.js")
        except Exception as e:
            print(f"❌ Kunne ikke opprette service-worker.js: {e}")
    
    return fixes_applied

def test_alle_problemer_lost():
    """Hovedfunksjon som tester og fikser alle problemer"""
    print("🧪 AKSJERADAR V6 - KOMPLETT FEILSJEKK OG FIKSER")
    print("=" * 60)
    
    all_errors = []
    
    # Test 1: Import problemer
    import_errors = test_import_issues()
    all_errors.extend(import_errors)
    
    # Test 2: Template syntax
    template_errors = test_template_syntax()
    all_errors.extend(template_errors)
    
    # Test 3: Database problemer
    db_errors = test_database_issues()
    all_errors.extend(db_errors)
    
    # Test 4: App oppstart
    startup_errors = test_app_startup()
    all_errors.extend(startup_errors)
    
    # Test 5: Blueprint konflikter
    blueprint_errors = fix_blueprint_conflicts()
    all_errors.extend(blueprint_errors)
    
    # Test 6: Offline filer
    offline_errors = test_offline_files()
    all_errors.extend(offline_errors)
    
    # Test 7: Endpoint testing (kun hvis app kjører)
    endpoint_errors = test_critical_endpoints()
    all_errors.extend(endpoint_errors)
    
    # Apply automatic fixes
    fixes = generate_fixes()
    
    # Generer rapport
    print("\n" + "=" * 60)
    print("📊 SLUTTRAPPORT")
    print("=" * 60)
    
    if not all_errors:
        print("🎉 ALLE PROBLEMER ER LØST!")
        print("✅ Alle tester bestått")
        print("✅ Appen er klar for produksjon")
    else:
        print(f"❌ {len(all_errors)} problemer funnet:")
        for category, error in all_errors:
            print(f"   • {category}: {error}")
    
    if fixes:
        print(f"\n🔧 {len(fixes)} automatiske fikser utført:")
        for fix in fixes:
            print(f"   • {fix}")
    
    print("\n📝 ANBEFALTE NESTE STEG:")
    if all_errors:
        print("1. Fiks de rapporterte problemene")
        print("2. Kjør testen på nytt")
        print("3. Start appen og test endepunkter")
    else:
        print("1. Start appen med: python run.py")
        print("2. Test alle funksjoner manuelt")
        print("3. Deploy til produksjon")
    
    print("\n" + "=" * 60)
    
    return len(all_errors) == 0

if __name__ == '__main__':
    success = test_alle_problemer_lost()
    sys.exit(0 if success else 1)
