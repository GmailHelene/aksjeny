#!/usr/bin/env python3
"""
Forenklet test av viktige endepunkter i Aksjeradar
"""
import requests
import json
from datetime import datetime

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def test_endpoints():
    """Test viktige endepunkter"""
    base_url = "http://localhost:5000"
    results = []
    
    # Liste over viktige endepunkter å teste
    important_endpoints = [
        # Hovedsider
        ("/", "Hovedside"),
        ("/demo", "Demo-side"),
        ("/login", "Innlogging"),
        ("/register", "Registrering"),
        ("/contact", "Kontakt"),
        ("/privacy", "Personvern"),
        ("/subscription", "Abonnement"),
        
        # API endepunkter
        ("/api/crypto", "Krypto API"),
        ("/api/currency", "Valuta API"),
        ("/api/oslo_stocks", "Oslo børs API"),
        ("/api/global_stocks", "Globale aksjer API"),
        ("/api/search", "Søk API"),
        
        # Stocks
        ("/stocks/", "Aksjer hovedside"),
        ("/stocks/list", "Aksjeliste"),
        ("/stocks/details/AAPL", "Apple detaljer"),
        ("/stocks/details/NHY.OL", "Norsk Hydro detaljer"),
        
        # Analysis
        ("/analysis/", "Analyse hovedside"),
        ("/analysis/ai", "AI analyse"),
        ("/analysis/market-overview", "Markedsoversikt"),
        
        # Portfolio
        ("/portfolio/", "Portefølje"),
        ("/portfolio/create", "Opprett portefølje"),
        
        # News
        ("/news/", "Nyheter"),
        ("/news/api/latest", "Siste nyheter API"),
        
        # Market Intel
        ("/market-intel/", "Markedsintelligens"),
        
        # Features
        ("/features/analyst-recommendations", "Analytiker anbefalinger"),
        
        # Static files
        ("/favicon.ico", "Favicon"),
        ("/manifest.json", "PWA manifest"),
        ("/service-worker.js", "Service worker"),
        ("/version", "Versjon"),
        
        # Debug endpoints
        ("/demo/ping", "Ping test"),
        ("/demo/user", "Brukerinfo"),
    ]
    
    print(f"{Color.BOLD}🧪 TESTING {len(important_endpoints)} VIKTIGE ENDEPUNKTER{Color.END}")
    print("=" * 80)
    print(f"Base URL: {base_url}")
    print(f"Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    passed = 0
    failed = 0
    
    for endpoint, description in important_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            # Vurder suksess basert på status kode
            if response.status_code in [200, 302, 401, 403]:
                status = "✅ PASS"
                color = Color.GREEN
                passed += 1
            else:
                status = "❌ FAIL"
                color = Color.RED
                failed += 1
            
            # Tilleggsinformasjon
            content_length = len(response.content) if response.content else 0
            response_time = response.elapsed.total_seconds()
            
            print(f"{color}{status} {endpoint:35} [{response.status_code:3}] {description:25} ({response_time:.2f}s, {content_length:,} bytes){Color.END}")
            
            results.append({
                'endpoint': endpoint,
                'description': description,
                'status_code': response.status_code,
                'success': response.status_code in [200, 302, 401, 403],
                'response_time': response_time,
                'content_length': content_length
            })
            
        except Exception as e:
            print(f"{Color.RED}❌ ERROR {endpoint:35} [---] {description:25} - {str(e)[:50]}{Color.END}")
            failed += 1
            results.append({
                'endpoint': endpoint,
                'description': description,
                'status_code': None,
                'success': False,
                'error': str(e)
            })
    
    # Sammendrag
    total = len(important_endpoints)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 80)
    print(f"{Color.BOLD}📊 SAMMENDRAG{Color.END}")
    print("=" * 80)
    print(f"Totalt testet:     {total}")
    print(f"{Color.GREEN}Bestått:          {passed} ({success_rate:.1f}%){Color.END}")
    print(f"{Color.RED}Feilet:           {failed}{Color.END}")
    
    if success_rate >= 90:
        print(f"\n{Color.GREEN}🎉 UTMERKET! Applikasjonen fungerer svært bra!{Color.END}")
    elif success_rate >= 75:
        print(f"\n{Color.YELLOW}👍 BRA! Applikasjonen fungerer godt med noen mindre problemer.{Color.END}")
    else:
        print(f"\n{Color.RED}⚠️  TRENGER ARBEID! Flere endepunkter har problemer.{Color.END}")
    
    # Vis feilede endepunkter
    failed_endpoints = [r for r in results if not r['success']]
    if failed_endpoints:
        print(f"\n{Color.RED}❌ FEILEDE ENDEPUNKTER:{Color.END}")
        for result in failed_endpoints:
            status = result.get('status_code', 'ERROR')
            error = result.get('error', '')
            print(f"{Color.RED}   {result['endpoint']:35} [{status}] {error[:60]}{Color.END}")
    
    # Lagre resultater
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"quick_endpoint_test_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tested': total,
            'passed': passed,
            'failed': failed,
            'success_rate': success_rate,
            'results': results
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n{Color.BLUE}📄 Resultater lagret til: {filename}{Color.END}")
    return success_rate > 75

if __name__ == "__main__":
    try:
        success = test_endpoints()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}🛑 Test avbrutt av bruker{Color.END}")
        exit(1)
    except Exception as e:
        print(f"\n{Color.RED}💥 Uventet feil: {e}{Color.END}")
        exit(1)
