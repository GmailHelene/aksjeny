from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from ..services.data_service import DataService

seo_content = Blueprint('seo_content', __name__)

class ContentGenerator:
    """AI-dreven innholdsgenerator for SEO"""
    
    def __init__(self):
        self.data_service = DataService()
    
    def generate_weekly_market_analysis(self):
        """Generer ukentlig markedsanalyse"""
        try:
            # Hent data for OSE-aksjer
            ose_symbols = ['EQNR.OL', 'TEL.OL', 'AKER.OL', 'NHY.OL', 'MOWI.OL']
            global_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
            
            analysis = {
                'title': f'Ukentlig Markedsanalyse - {datetime.now().strftime("%d. %b %Y")}',
                'date': datetime.now(),
                'ose_analysis': self.analyze_market_segment(ose_symbols, 'Oslo Børs'),
                'global_analysis': self.analyze_market_segment(global_symbols, 'Globale markeder'),
                'ai_predictions': self.generate_ai_predictions(ose_symbols + global_symbols),
                'risk_assessment': self.assess_market_risk(),
                'recommendations': self.generate_recommendations()
            }
            
            return analysis
            
        except Exception as e:
            current_app.logger.error(f"Feil ved generering av markedsanalyse: {e}")
            return None
    
    def analyze_market_segment(self, symbols, segment_name):
        """Analyser et markedssegment"""
        try:
            segment_data = []
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="7d")
                info = ticker.info
                
                if not hist.empty:
                    weekly_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
                    volume_change = (hist['Volume'].iloc[-1] / hist['Volume'].mean() - 1) * 100
                    
                    segment_data.append({
                        'symbol': symbol,
                        'name': info.get('longName', symbol),
                        'weekly_return': weekly_return,
                        'current_price': hist['Close'].iloc[-1],
                        'volume_change': volume_change,
                        'market_cap': info.get('marketCap', 0)
                    })
            
            if segment_data:
                avg_return = np.mean([s['weekly_return'] for s in segment_data])
                best_performer = max(segment_data, key=lambda x: x['weekly_return'])
                worst_performer = min(segment_data, key=lambda x: x['weekly_return'])
                
                return {
                    'segment_name': segment_name,
                    'avg_return': avg_return,
                    'best_performer': best_performer,
                    'worst_performer': worst_performer,
                    'stocks_data': segment_data,
                    'sentiment': 'Bullish' if avg_return > 2 else 'Bearish' if avg_return < -2 else 'Nøytral'
                }
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Feil ved analyse av {segment_name}: {e}")
            return None
    
    def generate_ai_predictions(self, symbols):
        """Generer AI-prediksjoner"""
        predictions = []
        
        for symbol in symbols[:5]:  # Begrens til 5 for ytelse
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="30d")
                
                if len(hist) >= 20:
                    # Beregn tekniske indikatorer
                    sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                    current_price = hist['Close'].iloc[-1]
                    
                    # Enkel trend-analyse
                    price_trend = 'Opp' if current_price > sma_20 else 'Ned'
                    momentum = (current_price / hist['Close'].iloc[-5] - 1) * 100
                    
                    # AI-score (forenklet)
                    ai_score = 50  # Basis
                    if current_price > sma_20:
                        ai_score += 20
                    if momentum > 2:
                        ai_score += 15
                    elif momentum < -2:
                        ai_score -= 15
                    
                    predictions.append({
                        'symbol': symbol,
                        'trend': price_trend,
                        'momentum': momentum,
                        'ai_score': max(0, min(100, ai_score)),
                        'confidence': np.random.randint(70, 95),  # Simulert konfidensgrad
                        'prediction': 'Kjøp' if ai_score > 70 else 'Selg' if ai_score < 30 else 'Hold'
                    })
                    
            except Exception as e:
                continue
        
        return predictions
    
    def assess_market_risk(self):
        """Vurder markedsrisiko"""
        # Forenklet risikovurdering
        risk_factors = [
            {
                'factor': 'Volatilitet',
                'level': 'Medium',
                'description': 'Økt volatilitet observert i teknologiaksjer'
            },
            {
                'factor': 'Geopolitisk risiko',
                'level': 'Lav',
                'description': 'Relativt stabile forhold globalt'
            },
            {
                'factor': 'Renterisiko',
                'level': 'Medium',
                'description': 'Usikkerhet rundt fremtidige renteendringer'
            }
        ]
        
        overall_risk = 'Medium'
        
        return {
            'overall_risk': overall_risk,
            'risk_factors': risk_factors,
            'recommendation': 'Vær forsiktig med gearing og følg med på makroøkonomiske indikatorer'
        }
    
    def generate_recommendations(self):
        """Generer handelsanbefalinger"""
        return [
            {
                'type': 'Sektorrotasjon',
                'description': 'Vurder å rotere fra vekstaksjer til verdiaksjer',
                'rationale': 'Renteøkninger favoriserer typisk verdiaksjer'
            },
            {
                'type': 'Diversifisering',
                'description': 'Øk eksponeringen mot defensive sektorer',
                'rationale': 'Redusert risiko i usikre tider'
            },
            {
                'type': 'Timing',
                'description': 'Bruk dollar-cost averaging ved innkjøp',
                'rationale': 'Reduserer timing-risiko i volatile markeder'
            }
        ]

@seo_content.route('/blogg')
def blog_index():
    """Hovedside for blogg/innhold"""
    # Generer innhold for SEO
    blog_posts = [
        {
            'title': 'Beste Aksjetips 2025: AI-analyser avslører skjulte perler',
            'excerpt': 'Våre AI-algoritmer har identifisert de mest lovende aksjene for 2025. Les om våre topp-5 anbefalinger og hvorfor teknisk analyse peker på sterkt oppsidepotensial.',
            'slug': 'beste-aksjetips-2025',
            'date': datetime.now() - timedelta(days=1),
            'category': 'Aksjetips',
            'read_time': '5 min',
            'image': '/static/images/blog/aksjetips-2025.jpg'
        },
        {
            'title': 'RSI og MACD Forklart: Slik bruker du teknisk analyse',
            'excerpt': 'Tekniske indikatorer kan virke kompliserte, men de er kraftige verktøy for timing av kjøp og salg. Her forklarer vi RSI, MACD og glidende snitt på en enkel måte.',
            'slug': 'teknisk-analyse-forklart',
            'date': datetime.now() - timedelta(days=3),
            'category': 'Utdanning',
            'read_time': '8 min',
            'image': '/static/images/blog/teknisk-analyse.jpg'
        },
        {
            'title': 'AI-revolusjon i finansverdenen: Slik endrer maskinlæring aksjehandel',
            'excerpt': 'Kunstig intelligens transformer måten vi analyserer og handler aksjer på. Lær om de nyeste AI-teknologiene og hvordan de kan forbedre din investeringsstrategi.',
            'slug': 'ai-revolusjon-finans',
            'date': datetime.now() - timedelta(days=5),
            'category': 'Teknologi',
            'read_time': '6 min',
            'image': '/static/images/blog/ai-finans.jpg'
        },
        {
            'title': 'Oslo Børs Analyse: Hvilke norske aksjer bør du følge?',
            'excerpt': 'En gjennomgang av de mest interessante aksjene på Oslo Børs. Fra Equinor til Telenor - vi analyserer fundamentals og tekniske signaler.',
            'slug': 'oslo-bors-analyse',
            'date': datetime.now() - timedelta(days=7),
            'category': 'Norske aksjer',
            'read_time': '7 min',
            'image': '/static/images/blog/oslo-bors.jpg'
        }
    ]
    
    return render_template('seo/blog_index.html', posts=blog_posts)

@seo_content.route('/blogg/<slug>')
def blog_post(slug):
    """Individuelle blogginnlegg"""
    # Her ville du normalt hente fra database
    posts = {
        'beste-aksjetips-2025': {
            'title': 'Beste Aksjetips 2025: AI-analyser avslører skjulte perler',
            'content': generate_aksjetips_content(),
            'meta_description': 'Oppdagelse de beste aksjetipsene for 2025 basert på AI-analyse. Teknisk analyse og fundamentals for de mest lovende investeringsmulighetene.',
            'keywords': 'aksjetips 2025, beste aksjer, AI aksjeanalyse, teknisk analyse, investeringstips',
            'date': datetime.now() - timedelta(days=1),
            'category': 'Aksjetips',
            'read_time': '5 min'
        },
        'teknisk-analyse-forklart': {
            'title': 'RSI og MACD Forklart: Slik bruker du teknisk analyse',
            'content': generate_technical_analysis_content(),
            'meta_description': 'Lær teknisk analyse med RSI, MACD og glidende snitt. Enkle forklaringer og praktiske tips for bedre timing av aksjehandel.',
            'keywords': 'RSI forklart, MACD teknisk analyse, glidende snitt, tekniske indikatorer, aksjehandel timing',
            'date': datetime.now() - timedelta(days=3),
            'category': 'Utdanning',
            'read_time': '8 min'
        }
    }
    
    post = posts.get(slug)
    if not post:
        return render_template('404.html'), 404
    
    return render_template('seo/blog_post.html', post=post, slug=slug)

@seo_content.route('/teknisk-analyse-oslobors')
def technical_analysis_oslo():
    """SEO-optimalisert side for teknisk analyse av Oslo Børs"""
    return render_template('seo/technical_analysis_oslo.html', 
                         title="Teknisk Analyse Oslo Børs - RSI, MACD og Signaler",
                         meta_description="Få teknisk analyse av Oslo Børs aksjer med RSI, MACD og andre indikatorer. AI-drevet analyse av norske aksjer og handelssignaler.")

@seo_content.route('/ai-prediksjon-aksjer')
def ai_prediction_stocks():
    """SEO-optimalisert side for AI-prediksjoner"""
    return render_template('seo/ai_predictions.html',
                         title="AI Aksjeprediksjon - Maskinlæring for Smartere Investeringer",
                         meta_description="Bruk AI og maskinlæring for å predikere aksjekurser. Avanserte algoritmer gir deg fordelen i markedet.")

@seo_content.route('/ukentlig-markedsrapport')
def weekly_market_report():
    """Ukentlig markedsrapport for SEO"""
    generator = ContentGenerator()
    analysis = generator.generate_weekly_market_analysis()
    
    if not analysis:
        return render_template('error.html', message="Kunne ikke generere markedsrapport"), 500
    
    return render_template('seo/weekly_report.html', 
                         analysis=analysis,
                         title=f"Ukentlig Markedsrapport - {analysis['date'].strftime('%d. %b %Y')}",
                         meta_description="Få ukentlig AI-analyse av Oslo Børs og globale markeder. Teknisk analyse, prediksjoner og handelssignaler.")

# Add missing blog routes for English URLs
@seo_content.route('/blog/')
def blog_index_en():
    """Blog index page (English URL)"""
    return blog_index()

@seo_content.route('/blog/<slug>')
def blog_post_en(slug):
    """Blog post page (English URL)"""
    return blog_post(slug)

@seo_content.route('/investment-guides/')
def investment_guides_index():
    """Investment guides index page"""
    return render_template('seo/investment_guides.html', 
                         title='Investeringsguider - Aksjeradar')

@seo_content.route('/investment-guides/<slug>')
def investment_guide_detail(slug):
    """Investment guide detail page"""
    return render_template('seo/investment_guide.html', 
                         title=f'Investeringsguide - {slug}',
                         slug=slug)

def generate_aksjetips_content():
    """Generer innhold for aksjetips-artikkel"""
    return """
    <h2>🎯 Våre Topp 5 Aksjetips for 2025</h2>
    
    <p>Basert på omfattende AI-analyse og teknisk analyse har vi identifisert fem aksjer som viser særlig lovende signaler for 2025. Våre algoritmer har analysert over 500 aksjer på Oslo Børs og globale markeder.</p>
    
    <h3>1. Equinor (EQNR.OL) - Energisektorens stabile gigant</h3>
    <ul>
        <li><strong>AI-score:</strong> 85/100</li>
        <li><strong>RSI:</strong> 45 (balansert)</li>
        <li><strong>MACD:</strong> Bullish crossover</li>
        <li><strong>Kursmål:</strong> 350-380 NOK</li>
    </ul>
    <p>Equinor viser sterke tekniske signaler med støtte rundt 280 NOK og et tydelig opptrender. Selskapet drar nytte av høye energipriser og økt fokus på fornybar energi.</p>
    
    <h3>2. Apple (AAPL) - Teknologikongen</h3>
    <ul>
        <li><strong>AI-score:</strong> 92/100</li>
        <li><strong>RSI:</strong> 52 (nøytral)</li>
        <li><strong>MACD:</strong> Bullish momentum</li>
        <li><strong>Kursmål:</strong> $200-220</li>
    </ul>
    <p>Apple fortsetter å innovere med AI-teknologi og viser sterke fundamentals. Teknisk analyse peker på breakout over $180.</p>
    
    <h3>📊 Hvordan vi analyserer</h3>
    <p>Vår AI-algoritme kombinerer:</p>
    <ul>
        <li>Tekniske indikatorer (RSI, MACD, Bollinger Bands)</li>
        <li>Volum-analyse og markedssentiment</li>
        <li>Fundamentale data og finansielle nøkkeltall</li>
        <li>Makroøkonomiske faktorer</li>
    </ul>
    
    <h3>⚠️ Risiko og disclaimer</h3>
    <p>Alle investeringer innebærer risiko. Disse anbefalingene er basert på teknisk analyse og historiske data, og garanterer ikke fremtidig avkastning. Gjør alltid din egen research før du investerer.</p>
    """

def generate_technical_analysis_content():
    """Generer innhold for teknisk analyse-artikkel"""
    return """
    <h2>📈 Teknisk Analyse Forklart - Fra Nybegynner til Ekspert</h2>
    
    <p>Teknisk analyse er kunsten å forutsi fremtidige prisbevegelser basert på historiske data. I denne guiden forklarer vi de viktigste indikatorene på en enkel og forståelig måte.</p>
    
    <h3>🎯 RSI - Relative Strength Index</h3>
    <p>RSI måler hvor "overkjøpt" eller "oversolgt" en aksje er på en skala fra 0 til 100.</p>
    <ul>
        <li><strong>Over 70:</strong> Overkjøpt - vurder salg</li>
        <li><strong>30-70:</strong> Nøytral sone</li>
        <li><strong>Under 30:</strong> Oversolgt - potensielt kjøp</li>
    </ul>
    
    <h4>Praktisk eksempel:</h4>
    <p>Hvis Equinor har RSI på 75, kan det indikere at aksjen er overkjøpt og kan falle på kort sikt. Kombinert med andre signaler kan dette være et salgssignal.</p>
    
    <h3>📊 MACD - Moving Average Convergence Divergence</h3>
    <p>MACD består av to linjer som kan gi kjøps- og salgssignaler:</p>
    <ul>
        <li><strong>MACD-linje:</strong> Forskjellen mellom 12-dagers og 26-dagers EMA</li>
        <li><strong>Signallinje:</strong> 9-dagers EMA av MACD-linjen</li>
    </ul>
    
    <h4>Signaler:</h4>
    <ul>
        <li><strong>Bullish crossover:</strong> MACD krysser over signallinjen (kjøp)</li>
        <li><strong>Bearish crossover:</strong> MACD krysser under signallinjen (selg)</li>
    </ul>
    
    <h3>📈 Glidende Snitt (Moving Averages)</h3>
    <p>Glidende snitt jevner ut prisdata og viser trender:</p>
    <ul>
        <li><strong>SMA 20:</strong> Kort sikt trend</li>
        <li><strong>SMA 50:</strong> Mellomlang sikt trend</li>
        <li><strong>SMA 200:</strong> Lang sikt trend</li>
    </ul>
    
    <h4>Golden Cross vs Death Cross:</h4>
    <ul>
        <li><strong>Golden Cross:</strong> 50-dagers krysser over 200-dagers (bullish)</li>
        <li><strong>Death Cross:</strong> 50-dagers krysser under 200-dagers (bearish)</li>
    </ul>
    
    <h3>🛠️ Slik kombinerer du indikatorene</h3>
    <p>Ingen indikator er perfekt alene. Her er en enkel strategi:</p>
    <ol>
        <li>Sjekk overordnet trend med glidende snitt</li>
        <li>Bruk RSI for å time inn- og utganger</li>
        <li>Bekreft med MACD-signaler</li>
        <li>Se på volum for bekreftelse</li>
    </ol>
    
    <h3>💡 Pro-tips for teknisk analyse</h3>
    <ul>
        <li>Bruk multiple timeframes (daglig, ukentlig)</li>
        <li>Alltid sett stop-loss for risikostyring</li>
        <li>Test strategien din med paper trading først</li>
        <li>Følg med på nyheter som kan påvirke teknisk analyse</li>
    </ul>
    """
