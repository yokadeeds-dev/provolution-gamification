/**
 * Provolution Challenges UI Component
 * Renders and manages the challenges section
 */

class ChallengesUI {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.challenges = [];
        this.activeChallenges = [];
        this.currentFilter = 'all';
        this.currentUser = null;

        this.init();
    }

    async init() {
        // Check if user is logged in
        if (ProvolutionAPI.isAuthenticated()) {
            try {
                this.currentUser = await ProvolutionAPI.user.getProfile();
                // Load active challenges for logged in users
                await this.loadActiveChallenges();
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

    async loadActiveChallenges() {
        if (!ProvolutionAPI.isAuthenticated()) {
            this.activeChallenges = [];
            return;
        }

        try {
            const response = await ProvolutionAPI.challenges.getActiveChallenges();
            this.activeChallenges = response.challenges || [];
        } catch (error) {
            console.error('Failed to load active challenges:', error);
            this.activeChallenges = [];
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

            if (e.target.classList.contains('view-progress-btn')) {
                const challengeId = e.target.dataset.challengeId;
                this.showChallengeProgress(challengeId);
            }

            if (e.target.classList.contains('complete-challenge-btn')) {
                const challengeId = e.target.dataset.challengeId;
                this.markComplete(challengeId);
            }
        });

        // Auth events
        window.addEventListener('auth:login', async () => {
            this.currentUser = await ProvolutionAPI.user.getProfile();
            await this.loadActiveChallenges();
            await this.loadChallenges();
        });
        window.addEventListener('auth:logout', () => {
            this.currentUser = null;
            this.activeChallenges = [];
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
            ${this.renderMyChallengesSection()}
            
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

    renderMyChallengesSection() {
        if (!this.currentUser || this.activeChallenges.length === 0) {
            return '';
        }

        return `
            <div class="my-challenges-section">
                <h2 class="section-title">📋 Meine aktiven Challenges</h2>
                <p class="section-subtitle">Dein Fortschritt bei laufenden Challenges</p>
                
                <div class="my-challenges-grid">
                    ${this.activeChallenges.map(c => this.renderActiveChallengeCard(c)).join('')}
                </div>
            </div>
        `;
    }

    renderActiveChallengeCard(challenge) {
        const progress = challenge.progress_percent || 0;
        const isCompletable = progress >= 100;

        return `
            <div class="active-challenge-card" data-challenge-id="${challenge.id}">
                <div class="active-challenge-header">
                    <span class="challenge-icon">${this.getCategoryIcon(challenge.category)}</span>
                    <h4>${challenge.name}</h4>
                </div>
                
                <div class="challenge-progress-container">
                    <div class="challenge-progress-bar">
                        <div class="challenge-progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <span class="challenge-progress-text">${progress}%</span>
                </div>
                
                <div class="active-challenge-meta">
                    <span>📅 ${challenge.days_remaining || 0} Tage übrig</span>
                    <span>🎯 ${challenge.xp_reward} XP</span>
                </div>
                
                <div class="active-challenge-actions">
                    <button class="btn-secondary view-progress-btn" data-challenge-id="${challenge.id}">
                        Fortschritt anzeigen
                    </button>
                    ${isCompletable ? `
                        <button class="btn-primary complete-challenge-btn" data-challenge-id="${challenge.id}">
                            ✅ Abschließen
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }

    getCategoryIcon(category) {
        const icons = {
            onboarding: '🌱',
            energie: '⚡',
            mobilitaet: '🚲',
            community: '🤝',
            politik: '🗳️'
        };
        return icons[category] || '🎯';
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
        const progress = challenge.progress_percent || 0;

        let ctaText = 'Challenge starten →';
        let ctaClass = 'challenge-cta';

        if (isJoined) {
            ctaText = 'Bereits dabei';
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
                
                ${isJoined ? `
                    <div class="challenge-progress-container">
                        <div class="challenge-progress-bar">
                            <div class="challenge-progress-fill" style="width: ${progress}%"></div>
                        </div>
                        <span class="challenge-progress-text">${progress}%</span>
                    </div>
                ` : ''}
                
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
        // Check if user is authenticated
        if (!ProvolutionAPI.isAuthenticated()) {
            this.showAuthModal();
            return;
        }

        const challenge = this.challenges.find(c => c.id === challengeId);

        if (!challenge) return;

        if (challenge.user_status === 'active') {
            // User is already joined, maybe show progress or nothing
            // For now, based on "Bereits dabei", we might just return or show info
            this.showNotification('Du bist bereits bei dieser Challenge dabei!', 'info');
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

            // Reload active challenges
            await this.loadActiveChallenges();

            // Re-render
            this.render();

            // Show success message
            this.showNotification(`🎉 ${result.message || 'Challenge erfolgreich beigetreten!'}`, 'success');
        } catch (error) {
            console.error('Join challenge error:', error);
            if (error.code === 'CHALLENGE_ALREADY_JOINED') {
                this.showNotification('Du nimmst bereits an dieser Challenge teil.', 'info');
                // Update state just in case
                challenge.user_status = 'active';
                this.render();
            } else {
                this.showNotification(error.message || 'Fehler beim Beitreten der Challenge.', 'error');
            }
        }
    }

    async trackProgress(challengeId, progressData) {
        if (!ProvolutionAPI.isAuthenticated()) {
            this.showAuthModal();
            return;
        }

        try {
            const result = await ProvolutionAPI.challenges.trackProgress(challengeId, progressData);

            // Update local state
            const challenge = this.challenges.find(c => c.id === challengeId);
            if (challenge && result.progress) {
                challenge.progress_percent = result.progress.progress_percent;
            }

            // Reload active challenges
            await this.loadActiveChallenges();

            // Re-render
            this.render();

            // Show notification
            let message = `Fortschritt aktualisiert: ${result.progress?.progress_percent || 0}%`;
            if (result.xp_earned > 0) {
                message += ` +${result.xp_earned} XP!`;
            }
            this.showNotification(message, 'success');

            return result;
        } catch (error) {
            console.error('Track progress error:', error);
            this.showNotification(error.message || 'Fehler beim Aktualisieren des Fortschritts.', 'error');
            throw error;
        }
    }

    async markComplete(challengeId) {
        if (!ProvolutionAPI.isAuthenticated()) {
            this.showAuthModal();
            return;
        }

        try {
            const result = await ProvolutionAPI.challenges.complete(challengeId);

            // Update local state
            const challenge = this.challenges.find(c => c.id === challengeId);
            if (challenge) {
                challenge.user_status = 'completed';
            }

            // Remove from active challenges
            this.activeChallenges = this.activeChallenges.filter(c => c.id !== challengeId);

            // Re-render
            this.render();

            // Show celebration
            this.showCompletionCelebration(challenge, result);

            // Emit event for XP update
            window.dispatchEvent(new CustomEvent('xp:earned', {
                detail: { xp: result.xp_earned, challengeId, challengeName: challenge?.name }
            }));

            return result;
        } catch (error) {
            console.error('Complete challenge error:', error);
            this.showNotification(error.message || 'Fehler beim Abschließen der Challenge.', 'error');
            throw error;
        }
    }

    showCompletionCelebration(challenge, result) {
        const xpEarned = result?.xp_earned || challenge?.xp_reward || 50;
        const badgeEarned = result?.badge_earned || challenge?.badge;

        const celebration = document.createElement('div');
        celebration.className = 'completion-celebration';
        celebration.innerHTML = `
            <div class="celebration-content">
                <div class="celebration-confetti">🎊</div>
                <h2>🎉 Challenge abgeschlossen!</h2>
                <p class="celebration-challenge-name">${challenge?.name || 'Challenge'}</p>
                
                <div class="celebration-rewards">
                    <div class="reward-xp">
                        <span class="reward-icon">⭐</span>
                        <span class="reward-value">+${xpEarned} XP</span>
                    </div>
                    ${badgeEarned ? `
                        <div class="reward-badge">
                            <span class="reward-icon">${badgeEarned.icon || '🏅'}</span>
                            <span class="reward-value">Badge: ${badgeEarned.name}</span>
                        </div>
                    ` : ''}
                </div>
                
                <button class="btn-primary celebration-close">Weiter 🚀</button>
            </div>
        `;

        document.body.appendChild(celebration);

        // Animate in
        setTimeout(() => celebration.classList.add('active'), 10);

        // Close button
        celebration.querySelector('.celebration-close').addEventListener('click', () => {
            celebration.classList.remove('active');
            setTimeout(() => celebration.remove(), 300);
        });

        // Auto-close after 5 seconds
        setTimeout(() => {
            if (celebration.parentElement) {
                celebration.classList.remove('active');
                setTimeout(() => celebration.remove(), 300);
            }
        }, 5000);
    }

    async showChallengeProgress(challengeId) {
        try {
            const progress = await ProvolutionAPI.challenges.getProgress(challengeId);
            const challenge = this.challenges.find(c => c.id === challengeId) ||
                this.activeChallenges.find(c => c.id === challengeId);

            // Show modal with progress
            this.showModal(`
                <div class="challenge-progress-modal">
                    <h3>${challenge?.name || 'Challenge'}</h3>
                    
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${progress.progress_percent}%"></div>
                        <span class="progress-text">${progress.progress_percent}%</span>
                    </div>
                    
                    <div class="progress-stats">
                        <div class="stat">
                            <span class="stat-value">${progress.days_completed || 0}</span>
                            <span class="stat-label">Tage geschafft</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${progress.days_remaining || 0}</span>
                            <span class="stat-label">Tage übrig</span>
                        </div>
                    </div>
                    
                    <div class="progress-actions">
                        <button class="btn-primary log-today-btn" data-challenge-id="${challengeId}">
                            ✅ Heute loggen
                        </button>
                        ${progress.progress_percent >= 100 ? `
                            <button class="btn-primary complete-challenge-btn" data-challenge-id="${challengeId}">
                                🏆 Challenge abschließen
                            </button>
                        ` : ''}
                    </div>
                </div>
            `);

            // Setup log button
            document.querySelector('.log-today-btn')?.addEventListener('click', () => {
                this.logTodayProgress(challengeId);
            });

            // Setup complete button
            document.querySelector('.modal-overlay .complete-challenge-btn')?.addEventListener('click', () => {
                this.closeModal();
                this.markComplete(challengeId);
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
            await this.loadActiveChallenges();
            await this.loadChallenges();

        } catch (error) {
            if (error.code === 'ALREADY_LOGGED') {
                this.showNotification('Du hast heute bereits geloggt.', 'info');
            } else {
                this.showNotification('Fehler beim Loggen.', 'error');
            }
        }
    }

    showAuthModal() {
        if (window.showLoginForm) {
            window.showLoginForm();
        } else {
            // Fallback if global function is missing
            this.showNotification('Bitte melde dich an, um fortzufahren.', 'info');
        }
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
