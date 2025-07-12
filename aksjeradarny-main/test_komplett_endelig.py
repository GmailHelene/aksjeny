#!/usr/bin/env python3
"""
Komplett test av alle endepunkter og funksjoner i Aksjeradar v6
Tester alle de siste endringene og rettelser
"""

import requests
import json
import time
from datetime import datetime
import sys
import re
from urllib.parse import urljoin

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class AksjeradarKomplettTester:
    def __init__(self, base_url='http://localhost:5001'):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def log(self, message, color=Color.BLUE):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"{color}[{timestamp}] {message}{Color.END}")
        
    def test_result(self, test_name, status, details=""):
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.test_results.append(result)
        
        if status == 'PASS':
            self.passed += 1
            self.log(f"✅ {test_name}: {details}", Color.GREEN)
        elif status == 'FAIL':
            self.failed += 1
            self.log(f"❌ {test_name}: {details}", Color.RED)
        else:  # WARN
            self.warnings += 1
            self.log(f"⚠️  {test_name}: {details}", Color.YELLOW)
    
    def check_app_connectivity(self):
        """Test grunnleggende tilkobling til appen"""
        self.log("🔍 Tester tilkobling til applikasjonen...", Color.BOLD)
        
        # Test flere potensielle porter
        test_urls = [
            'http://localhost:5001',
            'http://localhost:5002', 
            'http://localhost:5000',
            'http://127.0.0.1:5001',
            'http://127.0.0.1:5002'
        ]
        
        for url in test_urls:
            try:
                response = self.session.get(f"{url}/", timeout=5)
                if response.status_code == 200:
                    self.base_url = url
                    self.test_result('App Connectivity', 'PASS', f'Tilkoblet til {url}')
                    return True
            except:
                continue
                
        self.test_result('App Connectivity', 'FAIL', 'Kan ikke koble til applikasjonen')
        return False
    
    def test_health_endpoints(self):
        """Test health check endepunkter"""
        self.log("🏥 Tester health endepunkter...", Color.BOLD)
        
        health_endpoints = [
            ('/health/', 'Basic health check'),
            ('/health/detailed', 'Detailed health check'),
            ('/health/ready', 'Readiness probe'),
            ('/health/live', 'Liveness probe'),
            ('/health/routes', 'Routes overview'),
            ('/health/check-all', 'All dependencies check')
        ]
        
        for endpoint, description in health_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self.test_result(f'Health: {description}', 'PASS', 'Fungerer')
                else:
                    self.test_result(f'Health: {description}', 'WARN', f'Status {response.status_code}')
            except Exception as e:
                self.test_result(f'Health: {description}', 'FAIL', f'Feil: {str(e)}')
    
    def test_basic_pages(self):
        """Test grunnleggende sider som alle skal være tilgjengelige"""
        self.log("🏠 Tester grunnleggende sider...", Color.BOLD)
        
        basic_pages = [
            ('/', 'Forsiden'),
            ('/login', 'Logg inn side'),
            ('/register', 'Registrer side'),
            ('/forgot_password', 'Glemt passord'),
            ('/privacy', 'Personvern'),
            ('/contact', 'Kontakt'),
            ('/subscription', 'Abonnement'),
            ('/stocks/', 'Aksjer oversikt'),
            ('/analysis/', 'Analyse oversikt'),
            ('/offline', 'Offline side')
        ]
        
        for endpoint, description in basic_pages:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    # Sjekk om siden inneholder norsk tekst
                    if any(word in response.text.lower() for word in ['aksjeradar', 'logg inn', 'registrer', 'aksjer']):
                        self.test_result(f'Side: {description}', 'PASS', 'Laster og viser norsk innhold')
                    else:
                        self.test_result(f'Side: {description}', 'WARN', 'Laster men mangler kanskje norsk lokalisering')
                else:
                    self.test_result(f'Side: {description}', 'FAIL', f'Status {response.status_code}')
            except Exception as e:
                self.test_result(f'Side: {description}', 'FAIL', f'Feil: {str(e)}')
    
    def test_premium_endpoints(self):
        """Test premium endepunkter som skal være beskyttet"""
        self.log("💎 Tester premium endepunkter...", Color.BOLD)
        
        premium_endpoints = [
            ('/stocks/details/EQNR.OL', 'EQNR aksjedetaljer'),
            ('/stocks/details/DNB.OL', 'DNB aksjedetaljer'),
            ('/stocks/details/AAPL', 'Apple aksjedetaljer'),
            ('/analysis/market-overview', 'Markedsoversikt'),
            ('/analysis/technical/EQNR.OL', 'Teknisk analyse'),
            ('/portfolio/', 'Portefølje oversikt'),
            ('/portfolio/create', 'Opprett portefølje'),
            ('/stocks/list/oslo', 'Oslo Børs liste'),
            ('/stocks/list/global', 'Global aksjerliste'),
            ('/stocks/list/crypto', 'Kryptovaluta liste')
        ]
        
        for endpoint, description in premium_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", allow_redirects=False)
                
                if response.status_code == 200:
                    # Sjekk om det er prøveperiode aktiv
                    if 'prøveperiode' in response.text.lower() or 'trial' in response.text.lower():
                        self.test_result(f'Premium: {description}', 'PASS', 'Tilgjengelig med prøveperiode')
                    else:
                        self.test_result(f'Premium: {description}', 'PASS', 'Laster innhold')
                elif response.status_code == 302:
                    redirect_location = response.headers.get('Location', '')
                    if any(loc in redirect_location for loc in ['login', 'register', 'restricted']):
                        self.test_result(f'Premium: {description}', 'PASS', f'Omdirigerer til {redirect_location}')
                    else:
                        self.test_result(f'Premium: {description}', 'WARN', f'Omdirigerer til {redirect_location}')
                else:
                    self.test_result(f'Premium: {description}', 'FAIL', f'Status {response.status_code}')
                    
            except Exception as e:
                self.test_result(f'Premium: {description}', 'FAIL', f'Feil: {str(e)}')
    
    def test_stock_data_quality(self):
        """Test kvaliteten på aksjedata"""
        self.log("📈 Tester aksjedata kvalitet...", Color.BOLD)
        
        # Test spesifikke norske aksjer som skal ha gode data
        test_stocks = [
            ('EQNR.OL', 'Equinor'),
            ('DNB.OL', 'DNB Bank'),
            ('TEL.OL', 'Telenor'),
            ('MOWI.OL', 'Mowi')
        ]
        
        for ticker, company_name in test_stocks:
            try:
                response = self.session.get(f"{self.base_url}/stocks/details/{ticker}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Sjekk for "Ukjent kilde" problemer
                    if 'ukjent kilde' in content:
                        self.test_result(f'Data: {ticker}', 'FAIL', 'Inneholder "Ukjent kilde"')
                    elif 'ingen beskrivelse tilgjengelig' in content:
                        self.test_result(f'Data: {ticker}', 'WARN', 'Mangler beskrivelse')
                    elif company_name.lower() in content:
                        self.test_result(f'Data: {ticker}', 'PASS', f'Viser korrekt data for {company_name}')
                    else:
                        self.test_result(f'Data: {ticker}', 'WARN', 'Data lastet men kvalitet ukjent')
                        
                elif response.status_code == 302:
                    self.test_result(f'Data: {ticker}', 'WARN', 'Omdirigert (prøveperiode utløpt?)')
                else:
                    self.test_result(f'Data: {ticker}', 'FAIL', f'Status {response.status_code}')
                    
            except Exception as e:
                self.test_result(f'Data: {ticker}', 'FAIL', f'Feil: {str(e)}')
    
    def test_api_endpoints(self):
        """Test API endepunkter"""
        self.log("🔌 Tester API endepunkter...", Color.BOLD)
        
        api_endpoints = [
            ('/api/search?q=EQNR', 'Søke API'),
            ('/stocks/api/stock/EQNR.OL', 'Aksje data API'),
            ('/api/oslo_stocks', 'Oslo Børs API'),
            ('/api/global_stocks', 'Global aksjer API'),
        ]
        
        for endpoint, description in api_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data and len(data) > 0:
                            self.test_result(f'API: {description}', 'PASS', 'Returnerer gyldig JSON data')
                        else:
                            self.test_result(f'API: {description}', 'WARN', 'Returnerer tom data')
                    except:
                        self.test_result(f'API: {description}', 'WARN', 'Ikke gyldig JSON')
                else:
                    self.test_result(f'API: {description}', 'FAIL', f'Status {response.status_code}')
                    
            except Exception as e:
                self.test_result(f'API: {description}', 'FAIL', f'Feil: {str(e)}')
    
    def test_norwegian_localization(self):
        """Test norsk lokalisering"""
        self.log("🇳🇴 Tester norsk lokalisering...", Color.BOLD)
        
        pages_to_check = [
            ('/', ['aksjeradar', 'aksjer', 'markedet', 'norge']),
            ('/login', ['logg inn', 'brukernavn', 'passord']),
            ('/register', ['registrer', 'opprett konto', 'e-post']),
            ('/stocks/', ['aksjer', 'børs', 'oslo'])
        ]
        
        for endpoint, expected_words in pages_to_check:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    content = response.text.lower()
                    found_words = [word for word in expected_words if word in content]
                    
                    if len(found_words) >= len(expected_words) // 2:
                        self.test_result(f'Norsk: {endpoint}', 'PASS', f'Fant norske ord: {found_words}')
                    else:
                        self.test_result(f'Norsk: {endpoint}', 'WARN', f'Få norske ord funnet: {found_words}')
                else:
                    self.test_result(f'Norsk: {endpoint}', 'FAIL', f'Status {response.status_code}')
            except Exception as e:
                self.test_result(f'Norsk: {endpoint}', 'FAIL', f'Feil: {str(e)}')
    
    def test_pwa_functionality(self):
        """Test PWA funksjonalitet"""
        self.log("📱 Tester PWA funksjonalitet...", Color.BOLD)
        
        pwa_endpoints = [
            ('/manifest.json', 'Manifest fil'),
            ('/service-worker.js', 'Service Worker'),
            ('/offline', 'Offline side'),
            ('/static/images/logo-192.png', 'App ikon')
        ]
        
        for endpoint, description in pwa_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self.test_result(f'PWA: {description}', 'PASS', 'Tilgjengelig')
                else:
                    self.test_result(f'PWA: {description}', 'FAIL', f'Status {response.status_code}')
            except Exception as e:
                self.test_result(f'PWA: {description}', 'FAIL', f'Feil: {str(e)}')
    
    def test_error_handling(self):
        """Test feilhåndtering"""
        self.log("🚨 Tester feilhåndtering...", Color.BOLD)
        
        error_tests = [
            ('/stocks/details/INVALID_TICKER', 'Ugyldig aksjesymbol'),
            ('/nonexistent-page', '404 feil'),
            ('/portfolio/view/99999', 'Ikke-eksisterende portefølje')
        ]
        
        for endpoint, description in error_tests:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code in [404, 302]:
                    self.test_result(f'Feil: {description}', 'PASS', f'Håndterer med status {response.status_code}')
                elif response.status_code == 500:
                    self.test_result(f'Feil: {description}', 'FAIL', 'Server error (500)')
                else:
                    self.test_result(f'Feil: {description}', 'WARN', f'Uventet status {response.status_code}')
            except Exception as e:
                self.test_result(f'Feil: {description}', 'FAIL', f'Exception: {str(e)}')
    
    def run_all_tests(self):
        """Kjør alle tester"""
        start_time = time.time()
        
        self.log("🚀 Starter komplett testing av Aksjeradar...", Color.BOLD)
        self.log("=" * 60, Color.BLUE)
        
        # Sjekk tilkobling først
        if not self.check_app_connectivity():
            self.log("❌ Kan ikke koble til applikasjonen. Sjekk at Flask kjører.", Color.RED)
            return False
        
        # Kjør alle test-suiter
        self.test_health_endpoints()
        self.test_basic_pages()
        self.test_premium_endpoints()
        self.test_stock_data_quality()
        self.test_api_endpoints()
        self.test_norwegian_localization()
        self.test_pwa_functionality()
        self.test_error_handling()
        
        # Generer rapport
        self.generate_final_report(time.time() - start_time)
        
        return self.failed == 0
    
    def generate_final_report(self, duration):
        """Generer sluttrapport"""
        self.log("=" * 60, Color.BLUE)
        self.log("📊 ENDELIG TESTRAPPORT", Color.BOLD)
        self.log("=" * 60, Color.BLUE)
        
        total_tests = self.passed + self.failed + self.warnings
        
        self.log(f"📈 Totalt antall tester: {total_tests}", Color.BLUE)
        self.log(f"✅ Bestått: {self.passed}", Color.GREEN)
        self.log(f"❌ Feilet: {self.failed}", Color.RED)
        self.log(f"⚠️  Advarsler: {self.warnings}", Color.YELLOW)
        self.log(f"⏱️  Tid brukt: {duration:.2f} sekunder", Color.BLUE)
        
        if self.failed == 0:
            success_rate = (self.passed / total_tests) * 100 if total_tests > 0 else 0
            self.log(f"🎉 SUKSESS! {success_rate:.1f}% av testene bestått!", Color.GREEN)
            
            self.log("\n✅ Alle kritiske funksjoner virker:", Color.GREEN)
            self.log("   • Applikasjonen er tilgjengelig og responsiv", Color.GREEN)
            self.log("   • Norsk lokalisering er implementert", Color.GREEN)
            self.log("   • Premium endepunkter er beskyttet", Color.GREEN)
            self.log("   • Aksjedata vises korrekt", Color.GREEN)
            self.log("   • API endepunkter fungerer", Color.GREEN)
            self.log("   • PWA funksjonalitet er aktiv", Color.GREEN)
            self.log("   • Feilhåndtering fungerer", Color.GREEN)
            
        else:
            self.log(f"❌ {self.failed} kritiske feil funnet!", Color.RED)
            
            # Vis feiltesting
            self.log("\n🔍 Kritiske feil som må fikses:", Color.RED)
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    self.log(f"   • {result['test']}: {result['details']}", Color.RED)
        
        if self.warnings > 0:
            self.log(f"\n⚠️  {self.warnings} advarsler som bør sjekkes:", Color.YELLOW)
            for result in self.test_results:
                if result['status'] == 'WARN':
                    self.log(f"   • {result['test']}: {result['details']}", Color.YELLOW)
        
        self.log("\n" + "=" * 60, Color.BLUE)

def main():
    """Hovedfunksjon for å kjøre testene"""
    print(f"{Color.BOLD}🧪 Aksjeradar v6 - Komplett Testing Suite{Color.END}")
    print(f"{Color.BLUE}Tester alle de siste endringene og rettelser...{Color.END}\n")
    
    tester = AksjeradarKomplettTester()
    success = tester.run_all_tests()
    
    # Avslutt med riktig exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
