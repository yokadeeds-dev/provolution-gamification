/**
 * Provolution Leaderboard UI Component
 * Renders and manages the leaderboard section
 */

class LeaderboardUI {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentView = 'weekly';
        this.leaderboardData = null;
        
        this.init();
    }
    
    async init() {
        await this.loadLeaderboard();
        this.setupEventListeners();
    }
    
    async loadLeaderboard() {
        try {
            switch (this.currentView) {
                case 'weekly':
                    this.leaderboardData = await ProvolutionAPI.leaderboards.weekly(20);
                    break;
                case 'monthly':
                    this.leaderboardData = await ProvolutionAPI.leaderboards.monthly(20);
                    break;
                default:
                    this.leaderboardData = await ProvolutionAPI.leaderboards.weekly(20);
            }
            this.render();
        } catch (error) {
            console.error('Failed to load leaderboard:', error);
            this.showError();
        }
    }
    
    setupEventListeners() {
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('leaderboard-tab')) {
                this.setView(e.target.dataset.view);
            }
        });
    }
    
    setView(view) {
        this.currentView = view;
        
        this.container.querySelectorAll('.leaderboard-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.view === view);
        });
        
        this.loadLeaderboard();
    }
    
    render() {
        const data = this.leaderboardData;
        
        this.container.innerHTML = `
            <div class="leaderboard-section">
                <h2 class="section-title">🏆 Leaderboard</h2>
                
                <div class="leaderboard-tabs">
                    <button class="leaderboard-tab ${this.currentView === 'weekly' ? 'active' : ''}" data-view="weekly">
                        📅 Woche
                    </button>
                    <button class="leaderboard-tab ${this.currentView === 'monthly' ? 'active' : ''}" data-view="monthly">
                        📆 Monat
                    </button>
                </div>
                
                ${data?.period ? `
                    <div class="leaderboard-period">
                        ${this.formatDate(data.period.start)} - ${this.formatDate(data.period.end)}
                    </div>
                ` : ''}
                
                <div class="leaderboard-list">
                    ${this.renderRankings(data?.rankings || [])}
                </div>
                
                ${data?.my_rank ? this.renderMyRank(data.my_rank) : ''}
            </div>
        `;
    }
    
    renderRankings(rankings) {
        if (rankings.length === 0) {
            return `
                <div class="no-rankings">
                    <p>Noch keine Einträge in dieser Periode.</p>
                    <p>Sei der Erste! 🚀</p>
                </div>
            `;
        }
        
        return rankings.map((entry, index) => this.renderRankingEntry(entry, index)).join('');
    }
    
    renderRankingEntry(entry, index) {
        const medals = ['🥇', '🥈', '🥉'];
        const medal = index < 3 ? medals[index] : '';
        const rankClass = index < 3 ? `top-${index + 1}` : '';
        
        return `
            <div class="leaderboard-entry ${rankClass}">
                <div class="rank">
                    ${medal || `#${entry.rank}`}
                </div>
                <div class="user-info">
                    <span class="avatar">${entry.user.avatar_emoji || '🌱'}</span>
                    <span class="username">${entry.user.display_name || entry.user.username}</span>
                </div>
                <div class="score">
                    <span class="score-value">${Math.round(entry.score)}</span>
                    <span class="score-unit">kg CO₂</span>
                </div>
            </div>
        `;
    }
    
    renderMyRank(myRank) {
        return `
            <div class="my-rank-section">
                <h4>Dein Rang</h4>
                <div class="my-rank-card">
                    <div class="rank">#${myRank.rank}</div>
                    <div class="score">
                        <span class="score-value">${Math.round(myRank.score)}</span>
                        <span class="score-unit">kg CO₂</span>
                    </div>
                    <div class="position-info">
                        <span>${myRank.users_above} Nutzer vor dir</span>
                        <span>${myRank.users_below} Nutzer hinter dir</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('de-DE', { day: 'numeric', month: 'short' });
    }
    
    showError() {
        this.container.innerHTML = `
            <div class="leaderboard-error">
                <p>⚠️ Leaderboard konnte nicht geladen werden.</p>
                <button onclick="window.leaderboardUI.loadLeaderboard()">Neu laden</button>
            </div>
        `;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('leaderboard-container')) {
        window.leaderboardUI = new LeaderboardUI('leaderboard-container');
    }
});
