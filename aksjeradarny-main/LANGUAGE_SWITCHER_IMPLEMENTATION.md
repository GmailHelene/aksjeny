# Språkbytter Implementasjon - Komplett Guide

## 📍 Plassering av språkbytter

### 1. Footer (Hovedimplementasjon) ✅
```html
<footer class="footer mt-auto py-3 bg-dark">
    <div class="container">
        <div class="row">
            <div class="col-md-3">
                <h5>Språk / Language</h5>
                <div class="dropdown">
                    <button class="btn btn-outline-light dropdown-toggle" 
                            type="button" 
                            id="footerLanguageDropdown" 
                            data-bs-toggle="dropdown">
                        <i class="bi bi-globe"></i>
                        <span id="footer-current-language">NO</span>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-dark">
                        <li><a class="dropdown-item" href="#" onclick="switchLanguage('no')">
                            <i class="bi bi-flag"></i> Norsk
                        </a></li>
                        <li><a class="dropdown-item" href="#" onclick="switchLanguage('en')">
                            <i class="bi bi-flag-fill"></i> English
                        </a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</footer>
```

### 2. Brukerinnstillinger (Sekundær) ✅
```html
<!-- På profil/innstillinger side -->
<div class="card">
    <div class="card-header">
        <h5>Språkinnstillinger</h5>
    </div>
    <div class="card-body">
        <label for="language-select">Velg språk:</label>
        <select class="form-select" id="language-select" onchange="switchLanguage(this.value)">
            <option value="no" selected>Norsk</option>
            <option value="en">English</option>
        </select>
    </div>
</div>
```

## 🔧 JavaScript Implementasjon

### language-switcher.js
```javascript
// Bytt språk funksjon
function switchLanguage(language) {
    // Valider språk
    if (!['no', 'en'].includes(language)) return;
    
    // Lagre i localStorage
    localStorage.setItem('aksjeradar_language', language);
    
    // Send til server
    fetch('/api/language/switch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language: language })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Oppdater UI
            window.i18n.setLanguage(language);
            
            // Vis bekreftelse
            showLanguageChangeNotification(language);
            
            // Oppdater språkvisning
            updateLanguageDisplays(language);
        }
    })
    .catch(error => {
        console.error('Error switching language:', error);
    });
}

// Oppdater alle språkvisninger
function updateLanguageDisplays(language) {
    const displayText = language.toUpperCase();
    
    // Footer dropdown
    const footerLang = document.getElementById('footer-current-language');
    if (footerLang) footerLang.textContent = displayText;
    
    // Andre språkindikatorer
    document.querySelectorAll('.current-language-display').forEach(el => {
        el.textContent = displayText;
    });
}

// Vis notifikasjon om språkbytte
function showLanguageChangeNotification(language) {
    const message = language === 'en' ? 'Language changed to English' : 'Språk endret til norsk';
    
    // Bootstrap toast
    const toastHtml = `
        <div class="toast position-fixed bottom-0 end-0 m-3" role="alert">
            <div class="toast-body">
                <i class="bi bi-check-circle text-success me-2"></i>
                ${message}
            </div>
        </div>
    `;
    
    // Legg til og vis toast
    const toastContainer = document.createElement('div');
    toastContainer.innerHTML = toastHtml;
    document.body.appendChild(toastContainer);
    
    const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'));
    toast.show();
    
    // Fjern etter 3 sekunder
    setTimeout(() => {
        toastContainer.remove();
    }, 3000);
}

// Initialiser språk ved sidelasting
document.addEventListener('DOMContentLoaded', () => {
    const savedLanguage = localStorage.getItem('aksjeradar_language') || 'no';
    updateLanguageDisplays(savedLanguage);
});
```

## 🌐 Server-side Håndtering

### Flask routes
```python
@main.route('/api/language/switch', methods=['POST'])
def switch_language():
    """API endpoint for å bytte språk"""
    data = request.get_json()
    language = data.get('language', 'no')
    
    if language not in ['no', 'en']:
        return jsonify({'success': False, 'message': 'Invalid language'}), 400
    
    # Lagre i session
    session['language'] = language
    
    # Hvis bruker er innlogget, lagre i database
    if current_user.is_authenticated:
        current_user.preferred_language = language
        db.session.commit()
    
    return jsonify({
        'success': True,
        'language': language,
        'message': 'Språk endret' if language == 'no' else 'Language changed'
    })
```

## 📱 Responsive Design

### Mobile-vennlig footer
```css
/* Språkbytter responsive styling */
@media (max-width: 768px) {
    #footerLanguageDropdown {
        width: 100%;
        margin-top: 10px;
    }
    
    .footer .col-md-3 {
        text-align: center;
        margin-bottom: 20px;
    }
}
```

## 🔄 Automatisk språkdeteksjon

```javascript
// Detect browser language on first visit
function detectBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    
    // Sjekk om norsk
    if (browserLang.startsWith('no') || browserLang.startsWith('nb') || browserLang.startsWith('nn')) {
        return 'no';
    }
    
    // Standard til engelsk for alle andre
    return 'en';
}

// Bruk hvis ingen lagret preferanse
if (!localStorage.getItem('aksjeradar_language')) {
    const detectedLang = detectBrowserLanguage();
    switchLanguage(detectedLang);
}
```

## ✅ Testing

### Testscenarioer:
1. **Språkbytte i footer**: Klikk dropdown → velg språk → verifiser endring
2. **Persistens**: Bytt språk → refresh side → språk skal være lagret
3. **Innlogget bruker**: Språkvalg lagres i profil
4. **Ikke-innlogget**: Språkvalg lagres i localStorage
5. **API respons**: Sjekk at alle API-kall respekterer valgt språk

## 🎯 Resultat

- ✅ Språkbytter i footer (alltid synlig)
- ✅ Språkbytter i brukerinnstillinger
- ✅ Persistent språkvalg
- ✅ Smooth overgang mellom språk
- ✅ Ingen side-refresh nødvendig
- ✅ Fungerer for innloggede og ikke-innloggede brukere
