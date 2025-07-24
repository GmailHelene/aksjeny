/**
 * Enhanced Demo functionality for Aksjeradar
 */

// Global demo state
let demoProgress = {
    completedActions: [],
    currentStage: 'welcome'
};

function showDemo(section) {
    // Hide all demo sections
    document.querySelectorAll('.demo-section').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show the selected section
    const targetSection = document.getElementById(section + '-demo');
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Update active tab
    document.querySelectorAll('.demo-nav .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeTab = document.querySelector(`.demo-nav .btn[onclick="showDemo('${section}')"]`);
    if (activeTab) {
        activeTab.classList.add('active');
    }
}

// Demo AI Analysis - Interactive simulation
function demoAIAnalysis(ticker = 'EQNR.OL') {
    const resultDiv = document.getElementById('demo-ai-result') || createDemoResultDiv();
    
    // Show loading animation
    resultDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            Analyserer ${ticker} med AI...
        </div>
    `;
    
    // Simulate API call with delay
    setTimeout(() => {
        const aiResults = generateAIAnalysis(ticker);
        resultDiv.innerHTML = `
            <div class="card border-success">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0"><i class="bi bi-robot"></i> AI Analyse for ${ticker}</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Anbefaling: <span class="badge bg-success">${aiResults.recommendation}</span></h6>
                            <p><strong>Kursmål:</strong> ${aiResults.targetPrice} NOK</p>
                            <p><strong>Konfidens:</strong> ${aiResults.confidence}%</p>
                        </div>
                        <div class="col-md-6">
                            <h6>Nøkkelsignaler:</h6>
                            <ul class="list-unstyled">
                                ${aiResults.signals.map(signal => `<li><i class="bi bi-check-circle text-success"></i> ${signal}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                    <div class="mt-3">
                        <button class="btn btn-primary btn-sm" onclick="demoPortfolioAdd('${ticker}')">
                            <i class="bi bi-plus-circle"></i> Legg til i portefølje
                        </button>
                        <button class="btn btn-outline-secondary btn-sm ms-2" onclick="demoWatchlistAdd('${ticker}')">
                            <i class="bi bi-eye"></i> Legg til i watchlist
                        </button>
                    </div>
                </div>
            </div>
        `;
        markDemoComplete('ai-analysis');
    }, 2000);
}

// Demo Benjamin Graham Analysis
function demoGrahamAnalysis(ticker = 'DNB.OL') {
    const resultDiv = document.getElementById('demo-graham-result') || createDemoResultDiv();
    
    resultDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            Kjører Benjamin Graham analyse for ${ticker}...
        </div>
    `;
    
    setTimeout(() => {
        const grahamResults = generateGrahamAnalysis(ticker);
        resultDiv.innerHTML = `
            <div class="card border-warning">
                <div class="card-header bg-warning text-dark">
                    <h5 class="mb-0"><i class="bi bi-calculator"></i> Graham Analyse for ${ticker}</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="text-center">
                                <div class="display-4 text-warning">${grahamResults.score}</div>
                                <p class="text-muted">Graham Score</p>
                            </div>
                        </div>
                        <div class="col-md-8">
                            <h6>Verdivurdering:</h6>
                            <ul class="list-unstyled">
                                ${grahamResults.criteria.map(criteria => `
                                    <li><i class="bi bi-${criteria.passed ? 'check' : 'x'}-circle text-${criteria.passed ? 'success' : 'danger'}"></i> ${criteria.name}</li>
                                `).join('')}
                            </ul>
                            <p><strong>Intrinsic Value:</strong> ${grahamResults.intrinsicValue} NOK</p>
                            <p><strong>Current Price:</strong> ${grahamResults.currentPrice} NOK</p>
                            <p class="text-${grahamResults.upside > 0 ? 'success' : 'danger'}">
                                <strong>Upside Potential:</strong> ${grahamResults.upside}%
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        markDemoComplete('graham-analysis');
    }, 2500);
}

// Demo Warren Buffett Strategy
function demoWarrenBuffett(ticker = 'AAPL') {
    const resultDiv = document.getElementById('demo-buffett-result') || createDemoResultDiv();
    
    resultDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            Analyserer ${ticker} med Warren Buffett prinsipper...
        </div>
    `;
    
    setTimeout(() => {
        const buffettResults = generateBuffettAnalysis(ticker);
        resultDiv.innerHTML = `
            <div class="card border-primary">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="bi bi-trophy"></i> Buffett Analyse for ${ticker}</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Kvalitetsvurdering:</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-success" role="progressbar" style="width: ${buffettResults.qualityScore}%">${buffettResults.qualityScore}%</div>
                            </div>
                            <p><strong>ROE:</strong> ${buffettResults.roe}%</p>
                            <p><strong>Debt/Equity:</strong> ${buffettResults.debtRatio}</p>
                        </div>
                        <div class="col-md-6">
                            <h6>Konkurransefortrinn:</h6>
                            <ul class="list-unstyled">
                                ${buffettResults.moats.map(moat => `<li><i class="bi bi-shield-check text-success"></i> ${moat}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                    <div class="alert alert-${buffettResults.recommendation === 'KJØP' ? 'success' : 'warning'} mt-3">
                        <strong>Buffett Anbefaling:</strong> ${buffettResults.recommendation}
                        <br><small>${buffettResults.reasoning}</small>
                    </div>
                </div>
            </div>
        `;
        markDemoComplete('buffett-analysis');
    }, 2200);
}

// Demo Short Analysis
function demoShortAnalysis(ticker = 'TSLA') {
    const resultDiv = document.getElementById('demo-short-result') || createDemoResultDiv();
    
    resultDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            Analyserer short-muligheter for ${ticker}...
        </div>
    `;
    
    setTimeout(() => {
        const shortResults = generateShortAnalysis(ticker);
        resultDiv.innerHTML = `
            <div class="card border-danger">
                <div class="card-header bg-danger text-white">
                    <h5 class="mb-0"><i class="bi bi-graph-down"></i> Short Analyse for ${ticker}</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Short Indikatorer:</h6>
                            <p><strong>Short Interest:</strong> ${shortResults.shortInterest}%</p>
                            <p><strong>Borrow Rate:</strong> ${shortResults.borrowRate}%</p>
                            <p><strong>P/E Ratio:</strong> ${shortResults.peRatio}</p>
                        </div>
                        <div class="col-md-6">
                            <h6>Risikofaktorer:</h6>
                            <ul class="list-unstyled">
                                ${shortResults.risks.map(risk => `<li><i class="bi bi-exclamation-triangle text-warning"></i> ${risk}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                    <div class="alert alert-danger mt-3">
                        <strong>Short Rating:</strong> ${shortResults.rating}/10
                        <br><small>${shortResults.note}</small>
                    </div>
                </div>
            </div>
        `;
        markDemoComplete('short-analysis');
    }, 1800);
}

// Demo Portfolio Functions
function demoPortfolioAdd(ticker) {
    showToast(`${ticker} lagt til i demo-portefølje!`, 'success');
    markDemoComplete('portfolio-add');
}

function demoWatchlistAdd(ticker) {
    showToast(`${ticker} lagt til i watchlist!`, 'info');
    markDemoComplete('watchlist-add');
}

// Generate realistic demo data
function generateAIAnalysis(ticker) {
    const recommendations = ['KJØP', 'HOLD', 'SELG'];
    const signals = [
        'Sterk momentum i kursutviklingen',
        'Positiv teknisk analyse',
        'Gode fundamentale nøkkeltall',
        'Økt institusjonell interesse',
        'Sektor-momentum i favør'
    ];
    
    return {
        recommendation: recommendations[Math.floor(Math.random() * 2)], // Favor buy/hold
        targetPrice: (Math.random() * 200 + 50).toFixed(2),
        confidence: Math.floor(Math.random() * 30 + 70), // 70-100%
        signals: signals.slice(0, Math.floor(Math.random() * 3 + 2))
    };
}

function generateGrahamAnalysis(ticker) {
    const criteria = [
        { name: 'P/E < 15', passed: Math.random() > 0.3 },
        { name: 'P/B < 1.5', passed: Math.random() > 0.4 },
        { name: 'Debt/Equity < 0.5', passed: Math.random() > 0.5 },
        { name: 'Current Ratio > 2', passed: Math.random() > 0.4 },
        { name: 'Earnings Growth', passed: Math.random() > 0.3 }
    ];
    
    const passedCount = criteria.filter(c => c.passed).length;
    const score = Math.floor((passedCount / criteria.length) * 100);
    const currentPrice = Math.random() * 200 + 50;
    const intrinsicValue = currentPrice * (1 + (Math.random() * 0.4 - 0.2));
    
    return {
        score,
        criteria,
        currentPrice: currentPrice.toFixed(2),
        intrinsicValue: intrinsicValue.toFixed(2),
        upside: ((intrinsicValue - currentPrice) / currentPrice * 100).toFixed(1)
    };
}

function generateBuffettAnalysis(ticker) {
    const moats = [
        'Brand recognition',
        'Network effects',
        'Cost advantages',
        'High switching costs',
        'Regulatory protection'
    ];
    
    const qualityScore = Math.floor(Math.random() * 40 + 60); // 60-100%
    const selectedMoats = moats.slice(0, Math.floor(Math.random() * 3 + 2));
    
    return {
        qualityScore,
        roe: (Math.random() * 20 + 10).toFixed(1),
        debtRatio: (Math.random() * 0.8).toFixed(2),
        moats: selectedMoats,
        recommendation: qualityScore > 75 ? 'KJØP' : 'HOLD',
        reasoning: qualityScore > 75 ? 'Sterke konkurransefortrinn og god lønnsomhet' : 'Solid selskap, men venter på bedre pris'
    };
}

function generateShortAnalysis(ticker) {
    const risks = [
        'Høy volatilitet',
        'Squeeze potential',
        'Strong fundamentals',
        'Positive sentiment',
        'Technical support levels'
    ];
    
    const rating = Math.floor(Math.random() * 5 + 3); // 3-8
    
    return {
        shortInterest: (Math.random() * 30 + 5).toFixed(1),
        borrowRate: (Math.random() * 10 + 2).toFixed(1),
        peRatio: (Math.random() * 50 + 20).toFixed(1),
        risks: risks.slice(0, Math.floor(Math.random() * 3 + 2)),
        rating,
        note: rating > 6 ? 'Høy short-risiko, vær forsiktig' : 'Moderate short-muligheter'
    };
}

// Helper functions
function createDemoResultDiv() {
    const existingDiv = document.getElementById('demo-result-container');
    if (existingDiv) {
        return existingDiv;
    }
    
    const div = document.createElement('div');
    div.id = 'demo-result-container';
    div.className = 'mt-4';
    
    // Find a good place to insert it
    const contentArea = document.querySelector('.container') || document.body;
    contentArea.appendChild(div);
    
    return div;
}

function showToast(message, type = 'info') {
    // Create toast if it doesn't exist
    let toastContainer = document.getElementById('demo-toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'demo-toast-container';
        toastContainer.className = 'position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    const toastHtml = `
        <div class="toast show" role="alert">
            <div class="toast-header">
                <i class="bi bi-info-circle text-${type} me-2"></i>
                <strong class="me-auto">Demo</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        const toasts = toastContainer.querySelectorAll('.toast');
        if (toasts.length > 0) {
            toasts[0].remove();
        }
    }, 3000);
}

function markDemoComplete(action) {
    if (!demoProgress.completedActions.includes(action)) {
        demoProgress.completedActions.push(action);
        
        // Show progress
        if (demoProgress.completedActions.length >= 3) {
            showCTAModal();
        }
    }
}

function showCTAModal() {
    const modal = `
        <div class="modal fade" id="demoCompletionModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title"><i class="bi bi-check-circle"></i> Flott arbeid!</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <h6>Du har testet flere AI-analyser!</h6>
                        <p>Få tilgang til alle funksjoner og sanntidsdata med et premium-abonnement.</p>
                        <ul class="list-unstyled">
                            <li><i class="bi bi-check text-success"></i> Alle AI-analyser</li>
                            <li><i class="bi bi-check text-success"></i> Sanntids markedsdata</li>
                            <li><i class="bi bi-check text-success"></i> Avanserte screenere</li>
                            <li><i class="bi bi-check text-success"></i> Portfolio-tracking</li>
                        </ul>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Fortsett demo</button>
                        <a href="/subscription" class="btn btn-success">Start abonnement</a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('demoCompletionModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modal);
    
    // Show the modal
    const modalElement = new bootstrap.Modal(document.getElementById('demoCompletionModal'));
    modalElement.show();
}

// Interactive stock analysis
function showAnalysis(ticker) {
    demoAIAnalysis(ticker);
}

// Additional Demo Functions for Enhanced Interactivity

function demoScreener() {
    const resultDiv = document.getElementById('demo-result-container');
    
    resultDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            Kjører avansert aksje-screening...
        </div>
    `;
    
    setTimeout(() => {
        const screenerResults = generateScreenerResults();
        resultDiv.innerHTML = `
            <div class="card border-info">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0"><i class="bi bi-funnel"></i> Screener Resultater</h5>
                </div>
                <div class="card-body">
                    <p class="text-success"><strong>Fant ${screenerResults.length} aksjer som matcher dine kriterier:</strong></p>
                    <div class="table-responsive">
                        <table class="table table-sm table-hover">
                            <thead>
                                <tr>
                                    <th>Ticker</th>
                                    <th>Selskap</th>
                                    <th>Pris</th>
                                    <th>P/E</th>
                                    <th>RSI</th>
                                    <th>Signal</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${screenerResults.map(stock => `
                                    <tr>
                                        <td><strong>${stock.ticker}</strong></td>
                                        <td>${stock.company}</td>
                                        <td>${stock.price} NOK</td>
                                        <td>${stock.pe}</td>
                                        <td>${stock.rsi}</td>
                                        <td><span class="badge bg-${stock.signal === 'KJØP' ? 'success' : 'warning'}">${stock.signal}</span></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                    <div class="mt-3">
                        <button class="btn btn-primary btn-sm" onclick="window.location.href='/analysis/screener-view'">
                            <i class="bi bi-arrow-right"></i> Gå til full screener
                        </button>
                    </div>
                </div>
            </div>
        `;
        markDemoComplete('screener');
        updateDemoProgress();
    }, 2200);
}

function demoInsiderTrading() {
    const resultDiv = document.getElementById('demo-result-container');
    
    resultDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            Analyserer insider trading aktivitet...
        </div>
    `;
    
    setTimeout(() => {
        const insiderData = generateInsiderData();
        resultDiv.innerHTML = `
            <div class="card border-warning">
                <div class="card-header bg-warning text-dark">
                    <h5 class="mb-0"><i class="bi bi-person-badge"></i> Insider Trading Signaler</h5>
                </div>
                <div class="card-body">
                    <h6>Nylige transaksjoner fra innsidere:</h6>
                    <div class="row">
                        ${insiderData.map(transaction => `
                            <div class="col-md-6 mb-3">
                                <div class="card border-left-${transaction.type === 'KJØP' ? 'success' : 'danger'}">
                                    <div class="card-body p-3">
                                        <h6>${transaction.company} (${transaction.ticker})</h6>
                                        <p class="mb-1"><strong>${transaction.insider}</strong> - ${transaction.position}</p>
                                        <p class="mb-1">${transaction.type}: ${transaction.shares} aksjer</p>
                                        <p class="text-${transaction.type === 'KJØP' ? 'success' : 'danger'} mb-0">
                                            <strong>Verdi: ${transaction.value} NOK</strong>
                                        </p>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="alert alert-success mt-3">
                        <strong>Insider Sentiment:</strong> Bullish - 75% av transaksjoner er kjøp
                    </div>
                </div>
            </div>
        `;
        markDemoComplete('insider-trading');
        updateDemoProgress();
    }, 1800);
}

function demoPortfolioOptimization() {
    const resultDiv = document.getElementById('demo-result-container');
    
    resultDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            Optimaliserer din portefølje...
        </div>
    `;
    
    setTimeout(() => {
        const optimizationResults = generatePortfolioOptimization();
        resultDiv.innerHTML = `
            <div class="card border-success">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0"><i class="bi bi-pie-chart"></i> Portfolio Optimering</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Anbefalt allokering:</h6>
                            <div class="mb-2">
                                ${optimizationResults.allocation.map(item => `
                                    <div class="d-flex justify-content-between">
                                        <span>${item.sector}</span>
                                        <span><strong>${item.percentage}%</strong></span>
                                    </div>
                                    <div class="progress mb-2" style="height: 10px;">
                                        <div class="progress-bar bg-${item.color}" style="width: ${item.percentage}%"></div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>Forbedringspotensial:</h6>
                            <ul class="list-unstyled">
                                <li><i class="bi bi-arrow-up text-success"></i> Forventet avkastning: <strong>+${optimizationResults.expectedReturn}%</strong></li>
                                <li><i class="bi bi-shield text-primary"></i> Redusert risiko: <strong>-${optimizationResults.riskReduction}%</strong></li>
                                <li><i class="bi bi-graph-up text-warning"></i> Sharpe ratio: <strong>${optimizationResults.sharpeRatio}</strong></li>
                            </ul>
                            <div class="alert alert-light mt-3">
                                <small><strong>Diversifisering:</strong> Øk eksponeringen mot teknologi og reduser energi-vekting</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        markDemoComplete('portfolio-optimization');
        updateDemoProgress();
    }, 2500);
}

function demoRealTimeAlerts() {
    const resultDiv = document.getElementById('demo-result-container');
    
    resultDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            Setter opp sanntids varsler...
        </div>
    `;
    
    setTimeout(() => {
        const alertsData = generateRealTimeAlerts();
        resultDiv.innerHTML = `
            <div class="card border-danger">
                <div class="card-header bg-danger text-white">
                    <h5 class="mb-0"><i class="bi bi-bell"></i> Aktive Prisvarsler</h5>
                </div>
                <div class="card-body">
                    <h6>Dine personaliserte varsler:</h6>
                    ${alertsData.map(alert => `
                        <div class="alert alert-${alert.type === 'warning' ? 'warning' : 'info'} d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${alert.ticker}</strong> - ${alert.message}
                                <br><small class="text-muted">${alert.condition}</small>
                            </div>
                            <span class="badge bg-${alert.type === 'warning' ? 'warning' : 'primary'}">${alert.status}</span>
                        </div>
                    `).join('')}
                    
                    <div class="mt-3">
                        <h6>Smart AI Varsler:</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card bg-light">
                                    <div class="card-body p-3">
                                        <h6 class="card-title">🤖 AI Signal</h6>
                                        <p class="card-text small">EQNR.OL viser sterke kjøpssignaler basert på teknisk analyse</p>
                                        <span class="badge bg-success">Aktiv</span>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card bg-light">
                                    <div class="card-body p-3">
                                        <h6 class="card-title">📊 Volume Alert</h6>
                                        <p class="card-text small">Uvanlig høyt handelsvolum i DNB.OL</p>
                                        <span class="badge bg-info">Triggeret</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        markDemoComplete('real-time-alerts');
        updateDemoProgress();
    }, 1500);
}

function demoMarketAnalysis() {
    const resultDiv = document.getElementById('demo-result-container');
    
    resultDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            Analyserer markedstrends...
        </div>
    `;
    
    setTimeout(() => {
        resultDiv.innerHTML = `
            <div class="card border-primary">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="bi bi-graph-up"></i> AI Markedsanalyse</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="text-center">
                                <div class="text-success fs-1">📈</div>
                                <h6>Markedsstemning</h6>
                                <p class="text-success"><strong>Bullish</strong></p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="text-center">
                                <div class="text-warning fs-1">⚡</div>
                                <h6>Volatilitet</h6>
                                <p class="text-warning"><strong>Moderat</strong></p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="text-center">
                                <div class="text-info fs-1">🎯</div>
                                <h6>Handelsvolum</h6>
                                <p class="text-info"><strong>Høyt</strong></p>
                            </div>
                        </div>
                    </div>
                    <div class="alert alert-success mt-3">
                        <h6><i class="bi bi-lightbulb"></i> AI Anbefaling</h6>
                        <p class="mb-0">Markedet viser positive signaler med sterk momentum i teknologi-aksjer. Anbefaler økt posisjon i vekst-aksjer.</p>
                    </div>
                </div>
            </div>
        `;
        markDemoComplete('market-analysis');
        updateDemoProgress();
    }, 2000);
}

// Progress tracking functions
function updateDemoProgress() {
    const progressBar = document.getElementById('demo-progress-bar')?.querySelector('.progress-bar');
    const achievementsDiv = document.getElementById('demo-achievements');
    
    if (progressBar && achievementsDiv) {
        const completed = demoProgress.completedActions.length;
        const total = 8; // Total demo actions available
        const percentage = Math.min((completed / total) * 100, 100);
        
        progressBar.style.width = percentage + '%';
        progressBar.textContent = Math.round(percentage) + '%';
        
        if (completed >= 6) {
            achievementsDiv.innerHTML = `
                <div class="text-success">
                    <i class="bi bi-trophy"></i> Demo Mester! Du har testet ${completed}/${total} funksjoner
                    <br><small>Klar for premium?</small>
                </div>
            `;
        } else if (completed >= 3) {
            achievementsDiv.innerHTML = `
                <div class="text-info">
                    <i class="bi bi-star"></i> Bra! Du har testet ${completed}/${total} funksjoner
                    <br><small>Fortsett utforskningen!</small>
                </div>
            `;
        } else {
            achievementsDiv.innerHTML = `
                <div class="text-muted">
                    Du har testet ${completed}/${total} funksjoner
                    <br><small>Prøv flere analyser!</small>
                </div>
            `;
        }
    }
}

// Data generators for demo content
function generateScreenerResults() {
    const stocks = [
        { ticker: 'EQNR.OL', company: 'Equinor ASA', price: '284.50', pe: '12.4', rsi: '65', signal: 'KJØP' },
        { ticker: 'DNB.OL', company: 'DNB Bank ASA', price: '156.80', pe: '8.9', rsi: '58', signal: 'KJØP' },
        { ticker: 'TEL.OL', company: 'Telenor ASA', price: '134.20', pe: '15.2', rsi: '72', signal: 'HOLD' },
        { ticker: 'MOWI.OL', company: 'Mowi ASA', price: '198.60', pe: '18.7', rsi: '45', signal: 'KJØP' },
        { ticker: 'NHY.OL', company: 'Norsk Hydro ASA', price: '67.45', pe: '22.1', rsi: '52', signal: 'HOLD' }
    ];
    return stocks.slice(0, Math.floor(Math.random() * 3 + 3));
}

function generateInsiderData() {
    const transactions = [
        {
            ticker: 'EQNR.OL',
            company: 'Equinor ASA',
            insider: 'Anders Opedal',
            position: 'CEO',
            type: 'KJØP',
            shares: '5,000',
            value: '1,422,500'
        },
        {
            ticker: 'DNB.OL',
            company: 'DNB Bank ASA',
            insider: 'Kjerstin Braathen',
            position: 'CEO',
            type: 'KJØP',
            shares: '2,500',
            value: '392,000'
        },
        {
            ticker: 'TEL.OL',
            company: 'Telenor ASA',
            insider: 'Sigve Brekke',
            position: 'President & CEO',
            type: 'SALG',
            shares: '1,200',
            value: '161,040'
        }
    ];
    return transactions.slice(0, Math.floor(Math.random() * 2 + 2));
}

function generatePortfolioOptimization() {
    return {
        allocation: [
            { sector: 'Teknologi', percentage: 35, color: 'primary' },
            { sector: 'Finans', percentage: 25, color: 'success' },
            { sector: 'Energi', percentage: 20, color: 'warning' },
            { sector: 'Helse', percentage: 15, color: 'info' },
            { sector: 'Øvrig', percentage: 5, color: 'secondary' }
        ],
        expectedReturn: '12.5',
        riskReduction: '18',
        sharpeRatio: '1.45'
    };
}

function generateRealTimeAlerts() {
    return [
        {
            ticker: 'EQNR.OL',
            message: 'Pris over 280 NOK',
            condition: 'Trigger: >= 280.00 NOK',
            type: 'warning',
            status: 'Triggeret'
        },
        {
            ticker: 'DNB.OL',
            message: 'RSI under 30 (oversold)',
            condition: 'Trigger: RSI <= 30',
            type: 'info',
            status: 'Aktiv'
        },
        {
            ticker: 'AAPL',
            message: 'Volume spike detected',
            condition: 'Volume > 2x average',
            type: 'warning',
            status: 'Triggeret'
        }
    ];
}

// Initialize demo when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Show first demo section by default if available
    if (document.querySelector('.demo-section')) {
        showDemo('stocks');
    }
    
    // Initialize demo progress tracking
    demoProgress.currentStage = 'active';
    
    // Initialize progress display
    updateDemoProgress();
    
    console.log('Enhanced demo functionality loaded');
});
