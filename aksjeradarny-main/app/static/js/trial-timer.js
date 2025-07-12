/**
 * Trial Timer Management System
 * Handles trial expiration popups and notifications
 * Does NOT show timer in navigation (per user feedback)
 * Singleton pattern to prevent multiple instances
 */

class TrialTimerManager {
    static instance = null;
    
    constructor() {
        // Singleton pattern - only one instance allowed
        if (TrialTimerManager.instance) {
            return TrialTimerManager.instance;
        }
        
        this.timerInterval = null;
        this.trialStatus = null;
        this.initialized = false;
        
        TrialTimerManager.instance = this;
        
        this.initializeTimer();
    }

    async initializeTimer() {
        // Prevent multiple initializations
        if (this.initialized) {
            return;
        }
        this.initialized = true;
        
        try {
            // Don't show timer on demo page - demo shows expired message instead
            if (window.location.pathname === '/demo') {
                return;
            }
            
            // Don't show timer for premium/admin users
            if (document.body.classList.contains('user-subscribed') || 
                document.body.classList.contains('user-admin')) {
                return;
            }
            
            // Check if user is in trial mode
            const response = await fetch('/api/trial-status', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                this.trialStatus = await response.json();
                
                // Only show timer for active trial users (not unlimited access)
                if (this.trialStatus.active && !this.trialStatus.unlimited) {
                    // NO NAVIGATION TIMER - Only popup on expiration
                    this.startBackgroundTimer();
                }
            }
        } catch (error) {
            console.log('TrialTimerManager: Could not fetch trial status');
        }
    }

    // REMOVED: createTimerDisplay() - No more navigation timer

    startBackgroundTimer() {
        if (!this.trialStatus) return;

        // Calculate end time
        const startTime = new Date(this.trialStatus.start_time);
        const endTime = new Date(startTime.getTime() + 15 * 60 * 1000); // 15 minutes in milliseconds

        this.timerInterval = setInterval(() => {
            const now = new Date();
            const remaining = endTime - now;

            if (remaining <= 0) {
                // Trial expired - show popup
                this.showTrialExpiredMessage();
                clearInterval(this.timerInterval);
                return;
            }

            // Continue background monitoring - no UI updates needed
        }, 5000); // Check every 5 seconds instead of every second
    }

    showTrialExpiredMessage() {
        // Clear the timer interval first
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        
        // Check if popup was already shown in this session to prevent duplicates
        if (sessionStorage.getItem('trial_expired_popup_shown') === 'true') {
            return;
        }
        
        // Show popup modal for trial expiration
        this.showTrialExpiredPopup();
        
        // Mark popup as shown to prevent showing again in the same session
        sessionStorage.setItem('trial_expired_popup_shown', 'true');
        
        // Don't show additional notifications if popup was shown
        // Redirect to demo page after user dismisses popup or after timeout
        setTimeout(() => {
            if (!sessionStorage.getItem('trial_popup_dismissed')) {
                window.location.href = '/demo?source=trial_expired';
            }
        }, 30000); // 30 second timeout
    }
    
    showTrialExpiredPopup() {
        // Don't show popup if we're already on demo page
        if (window.location.pathname === '/demo') {
            return;
        }
        
        // Check if popup was already shown in this session
        if (sessionStorage.getItem('trial_expired_popup_shown') === 'true') {
            return;
        }
        
        // Create popup modal
        const popup = document.createElement('div');
        popup.className = 'modal fade';
        popup.id = 'trialExpiredModal';
        popup.setAttribute('data-bs-backdrop', 'static');
        popup.setAttribute('data-bs-keyboard', 'false');
        popup.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">
                            <i class="bi bi-clock-history"></i> Prøveperioden er utløpt
                        </h5>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-4">
                            <i class="bi bi-hourglass-bottom text-warning" style="font-size: 4rem;"></i>
                        </div>
                        <h6 class="mb-3">Din 15-minutters gratis prøveperiode er nå over!</h6>
                        <p class="mb-4">Du har nå begrenset tilgang til demo-funksjoner. For full tilgang til alle funksjoner, sanntidsdata og AI-analyser:</p>
                        
                        <div class="d-grid gap-2">
                            <a href="/register" class="btn btn-primary btn-lg">
                                <i class="bi bi-person-plus"></i> Opprett gratis konto
                            </a>
                            <a href="/subscription" class="btn btn-outline-primary">
                                <i class="bi bi-star"></i> Se abonnement (fra 199 kr/mnd)
                            </a>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="bi bi-arrow-left"></i> Fortsett med demo
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(popup);
        
        // Show the modal
        const modal = new bootstrap.Modal(popup, {
            backdrop: 'static',
            keyboard: false
        });
        modal.show();
        
        // Mark popup as shown
        sessionStorage.setItem('trial_expired_popup_shown', 'true');
        
        // Handle close events
        popup.addEventListener('hidden.bs.modal', () => {
            // Mark popup as dismissed
            sessionStorage.setItem('trial_popup_dismissed', 'true');
            // Redirect to demo page when popup is closed
            window.location.href = '/demo?source=trial_expired';
        });
        
        // Auto-close after 30 seconds if user doesn't interact
        setTimeout(() => {
            if (popup && document.body.contains(popup)) {
                modal.hide();
            }
        }, 30000);
    }

    destroy() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        // No timer element to remove anymore
    }
}

// Initialize trial timer when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if user might be in trial mode and not already initialized
    if (!document.body.classList.contains('user-subscribed') && 
        !document.body.classList.contains('user-admin') && 
        !window.trialTimerManager) {
        window.trialTimerManager = new TrialTimerManager();
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TrialTimerManager;
}
