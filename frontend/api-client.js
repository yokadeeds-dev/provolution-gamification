/**
 * Provolution Gamification API Client
 * Handles all communication with the backend API
 * 
 * Supports both local development and production (Render.com)
 */

// Auto-detect API URL based on environment
const API_BASE_URL = (() => {
    // Check if running on localhost
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8001/v1';
    }
    // Production: Use environment variable or default Render URL
    // This will be replaced during Netlify build or set via config
    return window.PROVOLUTION_API_URL || 'https://provolution-api.onrender.com/v1';
})();

console.log(`🌍 Provolution API: ${API_BASE_URL}`);

// Token management
let authToken = localStorage.getItem('provolution_token');

/**
 * Set authentication token
 */
function setToken(token) {
    authToken = token;
    localStorage.setItem('provolution_token', token);
}

/**
 * Clear authentication token
 */
function clearToken() {
    authToken = null;
    localStorage.removeItem('provolution_token');
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!authToken;
}

/**
 * Get current token
 */
function getToken() {
    return authToken;
}

/**
 * Make API request with proper headers
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        // Handle non-JSON responses
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            if (!response.ok) {
                throw {
                    status: response.status,
                    code: 'SERVER_ERROR',
                    message: `Server responded with status ${response.status}`
                };
            }
            return { success: true };
        }

        const data = await response.json();

        if (!response.ok) {
            throw {
                status: response.status,
                ...(data.error || { code: 'UNKNOWN_ERROR', message: 'Unknown error' })
            };
        }

        return data;
    } catch (error) {
        // Handle network errors
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw {
                status: 0,
                code: 'NETWORK_ERROR',
                message: 'Could not connect to server. Please check your internet connection.'
            };
        }

        if (error.code === 'UNAUTHORIZED') {
            clearToken();
            window.dispatchEvent(new CustomEvent('auth:logout'));
        }
        throw error;
    }
}

/**
 * Health check - verify API is reachable
 */
async function healthCheck() {
    try {
        const response = await fetch(`${API_BASE_URL.replace('/v1', '')}/health`);
        return response.ok;
    } catch {
        return false;
    }
}

// ============================================
// AUTH API
// ============================================

const AuthAPI = {
    /**
     * Register a new user
     */
    async register(username, email, password, options = {}) {
        const data = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({
                username,
                email,
                password,
                display_name: options.displayName,
                region: options.region,
                postal_code: options.postalCode,
                referral_code: options.referralCode
            })
        });

        if (data.token) {
            setToken(data.token);
        }

        return data;
    },

    /**
     * Login user
     */
    async login(email, password) {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        if (data.token) {
            setToken(data.token);
        }

        return data;
    },

    /**
     * Logout user
     */
    logout() {
        clearToken();
        window.dispatchEvent(new CustomEvent('auth:logout'));
    }
};

// ============================================
// USER API
// ============================================

const UserAPI = {
    /**
     * Get current user profile
     */
    async getProfile() {
        return apiRequest('/users/me');
    },

    /**
     * Update user profile
     */
    async updateProfile(updates) {
        return apiRequest('/users/me', {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    },

    /**
     * Get user stats
     */
    async getStats(userId) {
        return apiRequest(`/users/${userId}/stats`);
    }
};

// ============================================
// CHALLENGES API
// ============================================

const ChallengesAPI = {
    /**
     * List all challenges
     */
    async list(filters = {}) {
        const params = new URLSearchParams();
        if (filters.category) params.append('category', filters.category);
        if (filters.difficulty) params.append('difficulty', filters.difficulty);
        if (filters.status) params.append('status', filters.status);
        if (filters.limit) params.append('limit', filters.limit);
        if (filters.offset) params.append('offset', filters.offset);

        const query = params.toString();
        return apiRequest(`/challenges${query ? '?' + query : ''}`);
    },

    /**
     * Get challenge details
     */
    async get(challengeId) {
        return apiRequest(`/challenges/${challengeId}`);
    },

    /**
     * Join a challenge
     */
    async join(challengeId) {
        return apiRequest(`/challenges/${challengeId}/join`, {
            method: 'POST'
        });
    },

    /**
     * Log daily progress
     */
    async logProgress(challengeId, data) {
        return apiRequest(`/challenges/${challengeId}/log`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * Get user's progress on a challenge
     */
    async getProgress(challengeId) {
        return apiRequest(`/challenges/${challengeId}/progress`);
    },

    /**
     * Get user's active challenges
     */
    async getActiveChallenges() {
        return apiRequest('/user/challenges/active');
    },

    /**
     * Track progress on a challenge
     */
    async trackProgress(challengeId, progressData) {
        return apiRequest(`/challenges/${challengeId}/progress`, {
            method: 'POST',
            body: JSON.stringify(progressData)
        });
    },

    /**
     * Mark a challenge as complete
     */
    async complete(challengeId) {
        return apiRequest(`/challenges/${challengeId}/complete`, {
            method: 'POST'
        });
    }
};

// ============================================
// LEADERBOARDS API
// ============================================

const LeaderboardsAPI = {
    /**
     * Get weekly leaderboard
     */
    async weekly(limit = 10) {
        return apiRequest(`/leaderboards/weekly?limit=${limit}`);
    },

    /**
     * Get monthly leaderboard
     */
    async monthly(limit = 10) {
        return apiRequest(`/leaderboards/monthly?limit=${limit}`);
    },

    /**
     * Get regional leaderboard
     */
    async regional(region, limit = 10) {
        return apiRequest(`/leaderboards/regional/${region}?limit=${limit}`);
    }
};

// ============================================
// BADGES API
// ============================================

const BadgesAPI = {
    /**
     * List all badges
     */
    async list() {
        return apiRequest('/badges');
    },

    /**
     * Get user's badges
     */
    async myBadges() {
        return apiRequest('/badges/my');
    }
};

// ============================================
// REWARDS API
// ============================================

const RewardsAPI = {
    /**
     * List hardware packages
     */
    async listPackages() {
        return apiRequest('/rewards/packages');
    },

    /**
     * Redeem a package
     */
    async redeem(packageId, shippingAddress) {
        return apiRequest(`/rewards/redeem/${packageId}`, {
            method: 'POST',
            body: JSON.stringify({ shipping_address: shippingAddress })
        });
    }
};

// ============================================
// FOOTPRINT API
// ============================================

const FootprintAPI = {
    /**
     * Calculate CO2 footprint (anonymous)
     */
    async calculate(inputs) {
        return apiRequest('/footprint/calculate', {
            method: 'POST',
            body: JSON.stringify(inputs)
        });
    },

    /**
     * Get emission factors
     */
    async getFactors() {
        return apiRequest('/footprint/factors');
    },

    /**
     * Save footprint to user profile (requires auth)
     */
    async save(inputs) {
        return apiRequest('/footprint/me', {
            method: 'POST',
            body: JSON.stringify(inputs)
        });
    },

    /**
     * Get user's footprint history
     */
    async getHistory() {
        return apiRequest('/footprint/me');
    }
};

// ============================================
// EXPORT
// ============================================

window.ProvolutionAPI = {
    auth: AuthAPI,
    user: UserAPI,
    challenges: ChallengesAPI,
    leaderboards: LeaderboardsAPI,
    badges: BadgesAPI,
    rewards: RewardsAPI,
    footprint: FootprintAPI,
    isAuthenticated,
    getToken,
    setToken,
    clearToken,
    healthCheck,
    apiUrl: API_BASE_URL
};

console.log('🌍 Provolution API Client loaded');
