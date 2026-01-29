/**
 * Provolution Challenges UI Component
 * Renders and manages the challenges section
 */

class ChallengesUI {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.challenges = [];
        this.currentFilter = 'all';
        this.currentUser = null;
        
        this.init();
    }
    
    async init() {
        // Check if user is logged in
        if (ProvolutionAPI.isAuthenticated()) {
            try {
                this.currentUser = await ProvolutionAPI.user.getProfile();
            } catch (e) {
                console.log('Not authenticated');
            }
        }
        
        // Load challenges
        await this.loadChallenges();
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    async loadChallenges() {
        try {
            const response = await ProvolutionAPI.challenges.list({ limit: 50 });
            this.challenges = response.challenges;
            this.render();
        } catch (error) {
            console.error('Failed to load challenges:', error);
            this.showError('Challenges konnten nicht geladen werden.');
        }
    }
    
    setupEventListeners() {
        // Filter buttons
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-btn')) {
                this.setFilter(e.target.dataset.filter);
            }
            
            if (e.target.classList.contains('challenge-cta')) {
                const card = e.target.closest('.challenge-card');
                const challengeId = card.dataset.challengeId;
                this.handleJoinChallenge(challengeId);
            }
            
            if (e.target.classList.contains('challenge-details-btn')) {
                const card = e.target.closest('.challenge-card');
                const challengeId = card.dataset.challengeId;
                this.showChallengeDetails(challengeId);
            }
        });
        
        // Auth events
        window.addEventListener('auth:login', () => this.loadChallenges());
        window.addEventListener('auth:logout', () => {
            this.currentUser = null;
            this.loadChallenges();
        });
    }
    
    setFilter(category) {
        this.currentFilter = category;
        
        // Update active button
        this.container.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === category);
        });
        
        // Re-render challenges
        this.renderChallenges();
    }
    
    getFilteredChallenges() {
        if (this.currentFilter === 'all') {
            return this.challenges;
        }
        return this.challenges.filter(c => c.category === this.currentFilter);
    }
    
    render() {
        this.container.innerHTML = `
            <div class="challenges-section">
                <h2 class="section-title">🏆 Aktuelle Community-Challenges</h2>
                <p class="section-subtitle">
                    Nimm an Challenges teil, sammle XP und bewirke echten Impact!
                </p>
                
                <div class="challenge-filters">
                    <button class="filter-btn ${this.currentFilter === 'all' ? 'active' : ''}" data-filter="all">Alle</button>
                    <button class="filter-btn ${this.currentFilter === 'onboarding' ? 'active' : ''}" data-filter="onboarding">🌱 Einstieg</button>
                    <button class="filter-btn ${this.currentFilter === 'energie' ? 'active' : ''}" data-filter="energie">⚡ Energie</button>
                    <button class="filter-btn ${this.currentFilter === 'mobilitaet' ? 'active' : ''}" data-filter="mobilitaet">🚲 Mobilität</button>
                    <button class="filter-btn ${this.currentFilter === 'community' ? 'active' : ''}" data-filter="community">🤝 Community</button>
                    <button class="filter-btn ${this.currentFilter === 'politik' ? 'active' : ''}" data-filter="politik">🗳️ Politik</button>
                </div>
                
                <div class="challenge-grid" id="challenge-grid">
                    <!-- Challenges rendered here -->
                </div>
            </div>
        `;
        
        this.renderChallenges();
    }
    
    renderChallenges() {
        const grid = this.container.querySelector('#challenge-grid');
        const filtered = this.getFilteredChallenges();
        
        if (filtered.length === 0) {
            grid.innerHTML = `
                <div class="no-challenges">
                    <p>Keine Challenges in dieser Kategorie gefunden.</p>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = filtered.map(c => this.renderChallengeCard(c)).join('');
    }
    
    renderChallengeCard(challenge) {
        const difficultyLabels = {
            easy: 'Einfach',
            medium: 'Mittel',
            hard: 'Anspruchsvoll',
            expert: 'Experte'
        };
        
        const categoryIcons = {
            onboarding: '🌱',
            energie: '⚡',
            mobilitaet: '🚲',
            community: '🤝',
            politik: '🗳️'
        };
        
        const isJoined = challenge.user_status === 'active';
        const isCompleted = challenge.user_status === 'completed';
        
        let ctaText = 'Challenge starten →';
        let ctaClass = 'challenge-cta';
        
        if (isJoined) {
            ctaText = '📊 Fortschritt anzeigen';
            ctaClass = 'challenge-cta active';
        } else if (isCompleted) {
            ctaText = '✅ Abgeschlossen';
            ctaClass = 'challenge-cta completed';
        }
        
        return `
            <div class="challenge-card ${isJoined ? 'joined' : ''} ${isCompleted ? 'completed' : ''}" 
                 data-challenge-id="${challenge.id}" 
                 data-category="${challenge.category}">
                <div class="challenge-header">
                    <span class="challenge-icon">${categoryIcons[challenge.category] || '🎯'}</span>
                    <span class="challenge-difficulty ${challenge.difficulty}">
                        ${difficultyLabels[challenge.difficulty] || challenge.difficulty}
                    </span>
                    ${challenge.participants_count > 100 ? '<span class="challenge-featured-badge">⭐ Beliebt</span>' : ''}
                </div>
                
                <h3 class="challenge-title">${challenge.name}</h3>
                <p class="challenge-desc">${challenge.description}</p>
                
                <div class="challenge-meta">
                    <span class="challenge-duration">📅 ${challenge.duration_days} Tage</span>
                    <span class="challenge-xp">🎯 ${challenge.xp_reward} XP</span>
                </div>
                
                <div class="challenge-impact">
                    <span class="impact-label">CO₂-Ersparnis:</span>
                    <span class="impact-value">~${challenge.impact.co2_kg_year} kg/Jahr</span>
                </div>
                
                ${challenge.badge ? `
                    <div class="challenge-badge">
                        <span class="badge-preview">${challenge.badge.icon} Badge: "${challenge.badge.name}"</span>
                    </div>
                ` : ''}
                
                ${challenge.participants_count > 0 ? `
                    <div class="challenge-participants">
                        <span>👥 ${challenge.participants_count} Teilnehmer</span>
                    </div>
                ` : ''}
                
                <button class="${ctaClass}" ${isCompleted ? 'disabled' : ''}>${ctaText}</button>
            </div>
        `;
    }
    
    async handleJoinChallenge(challengeId) {
        if (!ProvolutionAPI.isAuthenticated()) {
            this.showLoginPrompt();
            return;
        }
        
        const challenge = this.challenges.find(c => c.id === challengeId);
        
        if (challenge.user_status === 'active') {
            // Show progress
            this.showChallengeProgress(challengeId);
            return;
        }
        
        if (challenge.user_status === 'completed') {
            return;
        }
        
        try {
            const result = await ProvolutionAPI.challenges.join(challengeId);
            
            // Update local state
            challenge.user_status = 'active';
            challenge.participants_count++;
            
            // Re-render
            this.renderChallenges();
            
            // Show success message
            this.showNotification(`🎉 ${result.message}`, 'success');
        } catch (error) {
            if (error.code === 'CHALLENGE_ALREADY_JOINED') {
                this.showNotification('Du nimmst bereits an dieser Challenge teil.', 'info');
            } else {
                this.showNotification('Fehler beim Beitreten der Challenge.', 'error');
            }
        }
    }
    
    async showChallengeProgress(challengeId) {
        try {
            const progress = await ProvolutionAPI.challenges.getProgress(challengeId);
            const challenge = this.challenges.find(c => c.id === challengeId);
            
            // Show modal with progress
            this.showModal(`
                <div class="challenge-progress-modal">
                    <h3>${challenge.name}</h3>
                    
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${progress.progress_percent}%"></div>
                        <span class="progress-text">${progress.progress_percent}%</span>
                    </div>
                    
                    <div class="progress-stats">
                        <div class="stat">
                            <span class="stat-value">${progress.days_completed}</span>
                            <span class="stat-label">Tage geschafft</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${progress.days_remaining}</span>
                            <span class="stat-label">Tage übrig</span>
                        </div>
                    </div>
                    
                    <button class="btn-primary log-today-btn" data-challenge-id="${challengeId}">
                        ✅ Heute loggen
                    </button>
                </div>
            `);
            
            // Setup log button
            document.querySelector('.log-today-btn').addEventListener('click', () => {
                this.logTodayProgress(challengeId);
            });
            
        } catch (error) {
            this.showNotification('Fortschritt konnte nicht geladen werden.', 'error');
        }
    }
    
    async logTodayProgress(challengeId) {
        try {
            const today = new Date().toISOString().split('T')[0];
            
            const result = await ProvolutionAPI.challenges.logProgress(challengeId, {
                log_date: today,
                completed: true,
                notes: ''
            });
            
            this.closeModal();
            
            let message = `Tag ${result.progress.days_completed} geschafft! 🎉`;
            if (result.xp_earned > 0) {
                message += ` +${result.xp_earned} XP verdient!`;
            }
            
            this.showNotification(message, 'success');
            
            // Reload challenges to update status
            await this.loadChallenges();
            
        } catch (error) {
            if (error.code === 'ALREADY_LOGGED') {
                this.showNotification('Du hast heute bereits geloggt.', 'info');
            } else {
                this.showNotification('Fehler beim Loggen.', 'error');
            }
        }
    }
    
    showLoginPrompt() {
        this.showModal(`
            <div class="login-prompt">
                <h3>🔐 Anmeldung erforderlich</h3>
                <p>Um an Challenges teilzunehmen, musst du dich anmelden.</p>
                <div class="modal-buttons">
                    <button class="btn-primary" onclick="showLoginForm()">Anmelden</button>
                    <button class="btn-secondary" onclick="showRegisterForm()">Registrieren</button>
                </div>
            </div>
        `);
    }
    
    showModal(content) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                ${content}
            </div>
        `;
        document.body.appendChild(modal);
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }
    
    closeModal() {
        document.querySelector('.modal-overlay')?.remove();
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    showError(message) {
        this.container.innerHTML = `
            <div class="error-message">
                <p>⚠️ ${message}</p>
                <button onclick="location.reload()">Neu laden</button>
            </div>
        `;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('challenges-container')) {
        window.challengesUI = new ChallengesUI('challenges-container');
    }
});
