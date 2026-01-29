/**
 * Provolution Auth UI Component
 * Handles login, registration, Google OAuth, and user state display
 */

// Google OAuth Client ID
const GOOGLE_CLIENT_ID = '249276087645-8db6c2913bgsv3p0p4c7njde3j5kvr6c.apps.googleusercontent.com';

class AuthUI {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentUser = null;
        this.googleInitialized = false;
        
        this.init();
    }
    
    async init() {
        // Load Google Identity Services
        this.loadGoogleScript();
        
        // Check if already logged in
        if (ProvolutionAPI.isAuthenticated()) {
            try {
                this.currentUser = await ProvolutionAPI.user.getProfile();
            } catch (e) {
                ProvolutionAPI.clearToken();
            }
        }
        
        this.render();
        this.setupEventListeners();
    }
    
    loadGoogleScript() {
        if (document.getElementById('google-gsi-script')) return;
        
        const script = document.createElement('script');
        script.id = 'google-gsi-script';
        script.src = 'https://accounts.google.com/gsi/client';
        script.async = true;
        script.defer = true;
        script.onload = () => this.initializeGoogle();
        document.head.appendChild(script);
    }
    
    initializeGoogle() {
        if (this.googleInitialized || !window.google) return;
        
        google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: (response) => this.handleGoogleCallback(response),
            auto_select: false,
            cancel_on_tap_outside: true
        });
        
        this.googleInitialized = true;
        console.log('✅ Google Sign-In initialized');
    }
    
    async handleGoogleCallback(response) {
        console.log('Google callback received');
        
        try {
            // Send the credential to our backend
            const result = await this.googleAuth(response.credential);
            
            this.currentUser = result.user;
            this.closeModal();
            this.render();
            
            window.dispatchEvent(new CustomEvent('auth:login', { detail: result.user }));
            
            const welcomeMsg = result.is_new_user 
                ? `Willkommen bei Provolution, ${result.user.display_name}! 🌍🎉`
                : `Willkommen zurück, ${result.user.display_name}! 🎉`;
            
            this.showNotification(welcomeMsg, 'success');
            
        } catch (error) {
            console.error('Google auth error:', error);
            this.showNotification('Google-Anmeldung fehlgeschlagen: ' + (error.message || 'Unbekannter Fehler'), 'error');
        }
    }
    
    async googleAuth(credential) {
        const API_BASE = window.PROVOLUTION_API_URL || 'https://provolution-api.onrender.com/v1';
        
        const response = await fetch(`${API_BASE}/auth/google/callback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ credential })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.error?.message || 'Google auth failed');
        }
        
        if (data.access_token) {
            ProvolutionAPI.setToken(data.access_token);
        }
        
        return data;
    }
    
    setupEventListeners() {
        window.addEventListener('auth:logout', () => {
            this.currentUser = null;
            this.render();
        });
    }
    
    render() {
        if (this.currentUser) {
            this.renderUserProfile();
        } else {
            this.renderAuthButtons();
        }
    }
    
    renderAuthButtons() {
        this.container.innerHTML = `
            <div class="auth-buttons">
                <button class="btn-login" onclick="window.authUI.showLoginForm()">Anmelden</button>
                <button class="btn-register" onclick="window.authUI.showRegisterForm()">Registrieren</button>
            </div>
        `;
    }
    
    renderUserProfile() {
        const user = this.currentUser;
        
        this.container.innerHTML = `
            <div class="user-profile-mini">
                <div class="user-avatar">${user.avatar_emoji || '🌱'}</div>
                <div class="user-info">
                    <span class="user-name">${user.display_name || user.username}</span>
                    <span class="user-xp">🎯 ${user.total_xp} XP • Level ${user.level}</span>
                </div>
                <div class="user-actions">
                    <button class="btn-profile" onclick="window.authUI.showProfile()">Profil</button>
                    <button class="btn-logout" onclick="window.authUI.logout()">Logout</button>
                </div>
            </div>
        `;
    }
    
    renderGoogleButton(containerId) {
        if (!window.google || !this.googleInitialized) {
            // Retry after script loads
            setTimeout(() => this.renderGoogleButton(containerId), 500);
            return;
        }
        
        const container = document.getElementById(containerId);
        if (!container) return;
        
        google.accounts.id.renderButton(container, {
            theme: 'outline',
            size: 'large',
            width: '100%',
            text: 'continue_with',
            shape: 'rectangular',
            logo_alignment: 'center'
        });
    }
    
    showLoginForm() {
        this.showModal(`
            <div class="auth-form">
                <h2>🔐 Anmelden</h2>
                
                <!-- Google Sign-In Button -->
                <div id="google-signin-btn" class="google-btn-container"></div>
                
                <div class="auth-divider">
                    <span>oder mit E-Mail</span>
                </div>
                
                <form id="login-form">
                    <div class="form-group">
                        <label for="login-email">E-Mail</label>
                        <input type="email" id="login-email" required placeholder="deine@email.de">
                    </div>
                    <div class="form-group">
                        <label for="login-password">Passwort</label>
                        <input type="password" id="login-password" required placeholder="••••••••">
                    </div>
                    <div class="form-error" id="login-error"></div>
                    <button type="submit" class="btn-primary">Anmelden</button>
                </form>
                <p class="auth-switch">
                    Noch kein Konto? 
                    <a href="#" onclick="window.authUI.closeModal(); window.authUI.showRegisterForm(); return false;">
                        Jetzt registrieren
                    </a>
                </p>
            </div>
        `);
        
        // Render Google button
        setTimeout(() => this.renderGoogleButton('google-signin-btn'), 100);
        
        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
    }
    
    showRegisterForm() {
        this.showModal(`
            <div class="auth-form">
                <h2>🌱 Registrieren</h2>
                
                <!-- Google Sign-In Button -->
                <div id="google-signup-btn" class="google-btn-container"></div>
                
                <div class="auth-divider">
                    <span>oder mit E-Mail</span>
                </div>
                
                <form id="register-form">
                    <div class="form-group">
                        <label for="reg-username">Benutzername</label>
                        <input type="text" id="reg-username" required placeholder="klimaheld123" 
                               pattern="[a-zA-Z0-9_]+" minlength="3" maxlength="30">
                        <small>Nur Buchstaben, Zahlen und _</small>
                    </div>
                    <div class="form-group">
                        <label for="reg-email">E-Mail</label>
                        <input type="email" id="reg-email" required placeholder="deine@email.de">
                    </div>
                    <div class="form-group">
                        <label for="reg-password">Passwort</label>
                        <input type="password" id="reg-password" required placeholder="••••••••" 
                               minlength="8">
                        <small>Min. 8 Zeichen</small>
                    </div>
                    <div class="form-group">
                        <label for="reg-region">Region (optional)</label>
                        <select id="reg-region">
                            <option value="">-- Wählen --</option>
                            <option value="NRW">Nordrhein-Westfalen</option>
                            <option value="BY">Bayern</option>
                            <option value="BW">Baden-Württemberg</option>
                            <option value="NI">Niedersachsen</option>
                            <option value="HE">Hessen</option>
                            <option value="SN">Sachsen</option>
                            <option value="RP">Rheinland-Pfalz</option>
                            <option value="BE">Berlin</option>
                            <option value="SH">Schleswig-Holstein</option>
                            <option value="BB">Brandenburg</option>
                            <option value="MV">Mecklenburg-Vorpommern</option>
                            <option value="TH">Thüringen</option>
                            <option value="ST">Sachsen-Anhalt</option>
                            <option value="HB">Bremen</option>
                            <option value="HH">Hamburg</option>
                            <option value="SL">Saarland</option>
                        </select>
                    </div>
                    <div class="form-error" id="register-error"></div>
                    <button type="submit" class="btn-primary">Konto erstellen</button>
                </form>
                <p class="auth-switch">
                    Bereits registriert? 
                    <a href="#" onclick="window.authUI.closeModal(); window.authUI.showLoginForm(); return false;">
                        Jetzt anmelden
                    </a>
                </p>
            </div>
        `);
        
        // Render Google button
        setTimeout(() => this.renderGoogleButton('google-signup-btn'), 100);
        
        document.getElementById('register-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });
    }
    
    async handleLogin() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const errorEl = document.getElementById('login-error');
        
        try {
            errorEl.textContent = '';
            const result = await ProvolutionAPI.auth.login(email, password);
            
            this.currentUser = result.user;
            this.closeModal();
            this.render();
            
            window.dispatchEvent(new CustomEvent('auth:login', { detail: result.user }));
            
            this.showNotification(`Willkommen zurück, ${result.user.display_name || result.user.username}! 🎉`, 'success');
            
        } catch (error) {
            errorEl.textContent = error.message || 'Anmeldung fehlgeschlagen.';
        }
    }
    
    async handleRegister() {
        const username = document.getElementById('reg-username').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        const region = document.getElementById('reg-region').value;
        const errorEl = document.getElementById('register-error');
        
        try {
            errorEl.textContent = '';
            
            const result = await ProvolutionAPI.auth.register(username, email, password, {
                region: region || undefined
            });
            
            // Login after successful registration
            const loginResult = await ProvolutionAPI.auth.login(email, password);
            this.currentUser = loginResult.user;
            
            this.closeModal();
            this.render();
            
            window.dispatchEvent(new CustomEvent('auth:login', { detail: loginResult.user }));
            
            this.showNotification(`Willkommen bei Provolution, ${username}! 🌍🎉`, 'success');
            
        } catch (error) {
            errorEl.textContent = error.message || 'Registrierung fehlgeschlagen.';
        }
    }
    
    showProfile() {
        const user = this.currentUser;
        const stats = user.stats || {};
        
        this.showModal(`
            <div class="profile-view">
                <div class="profile-header">
                    <span class="profile-avatar">${user.avatar_emoji || '🌱'}</span>
                    <h2>${user.display_name || user.username}</h2>
                    <span class="profile-level">Level ${user.level}</span>
                    ${user.google_id ? '<span class="google-badge">🔗 Google</span>' : ''}
                </div>
                
                <div class="profile-stats">
                    <div class="stat-card">
                        <span class="stat-value">${user.total_xp}</span>
                        <span class="stat-label">Gesamt XP</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">${stats.challenges_completed || 0}</span>
                        <span class="stat-label">Challenges</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">${Math.round(stats.total_co2_saved_kg || 0)}</span>
                        <span class="stat-label">kg CO₂ gespart</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">${stats.badges_earned || 0}</span>
                        <span class="stat-label">Badges</span>
                    </div>
                </div>
                
                <div class="profile-details">
                    <p><strong>Streak:</strong> ${user.streak_days} Tage 🔥</p>
                    <p><strong>Region:</strong> ${user.region || 'Nicht angegeben'}</p>
                    <p><strong>Referral-Code:</strong> <code>${user.referral_code || 'N/A'}</code></p>
                </div>
                
                <div class="profile-actions">
                    <button class="btn-secondary" onclick="window.authUI.showEditProfile()">
                        ✏️ Profil bearbeiten
                    </button>
                </div>
            </div>
        `);
    }
    
    showEditProfile() {
        const user = this.currentUser;
        
        this.showModal(`
            <div class="auth-form">
                <h2>✏️ Profil bearbeiten</h2>
                <form id="edit-profile-form">
                    <div class="form-group">
                        <label for="edit-displayname">Anzeigename</label>
                        <input type="text" id="edit-displayname" value="${user.display_name || ''}" 
                               placeholder="Dein Name">
                    </div>
                    <div class="form-group">
                        <label for="edit-avatar">Avatar Emoji</label>
                        <input type="text" id="edit-avatar" value="${user.avatar_emoji || '🌱'}" 
                               maxlength="2">
                    </div>
                    <div class="form-error" id="edit-error"></div>
                    <button type="submit" class="btn-primary">Speichern</button>
                </form>
            </div>
        `);
        
        document.getElementById('edit-profile-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleEditProfile();
        });
    }
    
    async handleEditProfile() {
        const displayName = document.getElementById('edit-displayname').value;
        const avatarEmoji = document.getElementById('edit-avatar').value;
        const errorEl = document.getElementById('edit-error');
        
        try {
            const updated = await ProvolutionAPI.user.updateProfile({
                display_name: displayName || undefined,
                avatar_emoji: avatarEmoji || undefined
            });
            
            this.currentUser = updated;
            this.closeModal();
            this.render();
            
            this.showNotification('Profil aktualisiert! ✅', 'success');
            
        } catch (error) {
            errorEl.textContent = error.message || 'Fehler beim Speichern.';
        }
    }
    
    logout() {
        // Also sign out from Google
        if (window.google && this.googleInitialized) {
            google.accounts.id.disableAutoSelect();
        }
        
        ProvolutionAPI.auth.logout();
        this.currentUser = null;
        this.render();
        this.showNotification('Erfolgreich abgemeldet. Bis bald! 👋', 'info');
    }
    
    showModal(content) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <button class="modal-close" onclick="window.authUI.closeModal()">×</button>
                ${content}
            </div>
        `;
        document.body.appendChild(modal);
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeModal();
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
}

// Global functions for onclick handlers
window.showLoginForm = () => window.authUI?.showLoginForm();
window.showRegisterForm = () => window.authUI?.showRegisterForm();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('auth-container')) {
        window.authUI = new AuthUI('auth-container');
    }
});
