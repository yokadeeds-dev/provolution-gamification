// footprint-ui.js - CO₂-Fußabdruck Rechner UI
/**
 * Provolution CO₂-Footprint Calculator
 * Multi-Step Wizard für die Berechnung des persönlichen CO₂-Fußabdrucks
 */

class FootprintCalculator {
    constructor(containerId, apiClient) {
        this.container = document.getElementById(containerId);
        this.api = apiClient;
        this.currentStep = 0;
        this.steps = ['housing', 'mobility', 'nutrition', 'consumption', 'result'];
        this.data = this.getDefaultData();
        this.result = null;
        this.isAuthenticated = false;
    }

    getDefaultData() {
        return {
            housing: {
                housing_type: 'apartment',
                housing_size_sqm: 80,
                household_members: 2,
                heating_type: 'gas',
                heating_consumption_kwh: null,
                electricity_kwh: null,
                green_electricity: false
            },
            mobility: {
                has_car: false,
                car_fuel_type: null,
                car_km_year: 0,
                car_consumption_l_100km: null,
                public_transport_km_year: 2000,
                bike_km_year: 500,
                flights_short_haul: 0,
                flights_long_haul: 0
            },
            nutrition: {
                diet_type: 'mixed',
                regional_seasonal: false,
                food_waste_level: 'medium'
            },
            consumption: {
                shopping_frequency: 'moderate',
                secondhand_preference: false,
                digital_consumption: 'medium'
            }
        };
    }

    init(isAuthenticated = false) {
        this.isAuthenticated = isAuthenticated;

        // Listen for auth events
        window.addEventListener('auth:login', (e) => this.handleAuthChange(true, e.detail));
        window.addEventListener('auth:logout', () => this.handleAuthChange(false));

        this.render();
    }

    handleAuthChange(isAuthenticated, user = null) {
        console.log(`🔄 FootprintCalculator: Auth changed -> ${isAuthenticated ? 'Logged In' : 'Logged Out'}`);
        this.isAuthenticated = isAuthenticated;

        if (user && user.token) {
            // Update API client token if needed (though typically handled by ProvolutionAPI)
            if (this.api && !this.api.getToken()) {
                this.api.setToken(user.token);
            }
        }

        // If we're on the result step, we need to recalculate (to save data) and re-render
        if (this.steps[this.currentStep] === 'result') {
            this.calculate().then(() => this.render());
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="footprint-calculator">
                <div class="calc-header">
                    <h2>🌍 Dein CO₂-Fußabdruck</h2>
                    <p>Berechne in 4 Schritten deinen persönlichen Klimaimpact</p>
                </div>
                
                <div class="progress-bar">
                    ${this.renderProgressBar()}
                </div>
                
                <div class="calc-content">
                    ${this.renderCurrentStep()}
                </div>
                
                <div class="calc-navigation">
                    ${this.renderNavigation()}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    renderProgressBar() {
        const labels = ['🏠 Wohnen', '🚗 Mobilität', '🥗 Ernährung', '🛒 Konsum', '📊 Ergebnis'];
        return labels.map((label, i) => `
            <div class="progress-step ${i === this.currentStep ? 'active' : ''} ${i < this.currentStep ? 'completed' : ''}">
                <span class="step-number">${i + 1}</span>
                <span class="step-label">${label}</span>
            </div>
        `).join('<div class="progress-line"></div>');
    }

    renderCurrentStep() {
        switch (this.steps[this.currentStep]) {
            case 'housing': return this.renderHousingStep();
            case 'mobility': return this.renderMobilityStep();
            case 'nutrition': return this.renderNutritionStep();
            case 'consumption': return this.renderConsumptionStep();
            case 'result': return this.renderResultStep();
            default: return '';
        }
    }

    renderHousingStep() {
        const d = this.data.housing;
        return `
            <div class="step-content">
                <h3>🏠 Wohnen & Energie</h3>
                
                <div class="form-group">
                    <label>Wohnform</label>
                    <div class="radio-group">
                        <label class="radio-card ${d.housing_type === 'apartment' ? 'selected' : ''}">
                            <input type="radio" name="housing_type" value="apartment" ${d.housing_type === 'apartment' ? 'checked' : ''}>
                            <span class="icon">🏢</span>
                            <span class="text">Wohnung</span>
                        </label>
                        <label class="radio-card ${d.housing_type === 'house' ? 'selected' : ''}">
                            <input type="radio" name="housing_type" value="house" ${d.housing_type === 'house' ? 'checked' : ''}>
                            <span class="icon">🏠</span>
                            <span class="text">Haus</span>
                        </label>
                        <label class="radio-card ${d.housing_type === 'shared' ? 'selected' : ''}">
                            <input type="radio" name="housing_type" value="shared" ${d.housing_type === 'shared' ? 'checked' : ''}>
                            <span class="icon">👥</span>
                            <span class="text">WG</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Wohnfläche (m²)</label>
                        <input type="range" name="housing_size_sqm" min="20" max="250" value="${d.housing_size_sqm}" class="slider">
                        <span class="slider-value">${d.housing_size_sqm} m²</span>
                    </div>
                    <div class="form-group">
                        <label>Personen im Haushalt</label>
                        <input type="range" name="household_members" min="1" max="6" value="${d.household_members}" class="slider">
                        <span class="slider-value">${d.household_members}</span>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Heizungsart</label>
                    <select name="heating_type" class="select-input">
                        <option value="gas" ${d.heating_type === 'gas' ? 'selected' : ''}>🔥 Gas</option>
                        <option value="oil" ${d.heating_type === 'oil' ? 'selected' : ''}>🛢️ Öl</option>
                        <option value="district" ${d.heating_type === 'district' ? 'selected' : ''}>🏭 Fernwärme</option>
                        <option value="heatpump" ${d.heating_type === 'heatpump' ? 'selected' : ''}>♨️ Wärmepumpe</option>
                        <option value="wood" ${d.heating_type === 'wood' ? 'selected' : ''}>🪵 Holz/Pellets</option>
                        <option value="electric" ${d.heating_type === 'electric' ? 'selected' : ''}>⚡ Elektro</option>
                    </select>
                </div>
                
                <div class="form-group checkbox-group">
                    <label class="checkbox-card ${d.green_electricity ? 'selected' : ''}">
                        <input type="checkbox" name="green_electricity" ${d.green_electricity ? 'checked' : ''}>
                        <span class="icon">🌱</span>
                        <span class="text">Ich nutze Ökostrom</span>
                    </label>
                </div>
            </div>
        `;
    }

    renderMobilityStep() {
        const d = this.data.mobility;
        return `
            <div class="step-content">
                <h3>🚗 Mobilität</h3>
                
                <div class="form-group checkbox-group">
                    <label class="checkbox-card ${d.has_car ? 'selected' : ''}">
                        <input type="checkbox" name="has_car" ${d.has_car ? 'checked' : ''}>
                        <span class="icon">🚗</span>
                        <span class="text">Ich habe ein Auto</span>
                    </label>
                </div>
                
                <div class="car-details ${d.has_car ? '' : 'hidden'}">
                    <div class="form-group">
                        <label>Antriebsart</label>
                        <div class="radio-group small">
                            <label class="radio-card ${d.car_fuel_type === 'petrol' ? 'selected' : ''}">
                                <input type="radio" name="car_fuel_type" value="petrol" ${d.car_fuel_type === 'petrol' ? 'checked' : ''}>
                                <span class="text">⛽ Benzin</span>
                            </label>
                            <label class="radio-card ${d.car_fuel_type === 'diesel' ? 'selected' : ''}">
                                <input type="radio" name="car_fuel_type" value="diesel" ${d.car_fuel_type === 'diesel' ? 'checked' : ''}>
                                <span class="text">🛢️ Diesel</span>
                            </label>
                            <label class="radio-card ${d.car_fuel_type === 'hybrid' ? 'selected' : ''}">
                                <input type="radio" name="car_fuel_type" value="hybrid" ${d.car_fuel_type === 'hybrid' ? 'checked' : ''}>
                                <span class="text">🔋 Hybrid</span>
                            </label>
                            <label class="radio-card ${d.car_fuel_type === 'electric' ? 'selected' : ''}">
                                <input type="radio" name="car_fuel_type" value="electric" ${d.car_fuel_type === 'electric' ? 'checked' : ''}>
                                <span class="text">⚡ Elektro</span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Kilometer pro Jahr</label>
                        <input type="range" name="car_km_year" min="0" max="40000" step="1000" value="${d.car_km_year}" class="slider">
                        <span class="slider-value">${d.car_km_year.toLocaleString('de')} km</span>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>ÖPNV (km/Jahr)</label>
                    <input type="range" name="public_transport_km_year" min="0" max="20000" step="500" value="${d.public_transport_km_year}" class="slider">
                    <span class="slider-value">${d.public_transport_km_year.toLocaleString('de')} km</span>
                </div>
                
                <div class="form-group">
                    <label>Fahrrad (km/Jahr)</label>
                    <input type="range" name="bike_km_year" min="0" max="10000" step="100" value="${d.bike_km_year}" class="slider">
                    <span class="slider-value">${d.bike_km_year.toLocaleString('de')} km 🚲</span>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>✈️ Kurzstreckenflüge (&lt;3h)</label>
                        <input type="range" name="flights_short_haul" min="0" max="20" value="${d.flights_short_haul}" class="slider">
                        <span class="slider-value">${d.flights_short_haul} Flüge/Jahr</span>
                    </div>
                    <div class="form-group">
                        <label>🌍 Langstreckenflüge (&gt;3h)</label>
                        <input type="range" name="flights_long_haul" min="0" max="10" value="${d.flights_long_haul}" class="slider">
                        <span class="slider-value">${d.flights_long_haul} Flüge/Jahr</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderNutritionStep() {
        const d = this.data.nutrition;
        return `
            <div class="step-content">
                <h3>🥗 Ernährung</h3>
                
                <div class="form-group">
                    <label>Ernährungsweise</label>
                    <div class="radio-group vertical">
                        <label class="radio-card ${d.diet_type === 'vegan' ? 'selected' : ''}">
                            <input type="radio" name="diet_type" value="vegan" ${d.diet_type === 'vegan' ? 'checked' : ''}>
                            <span class="icon">🌱</span>
                            <span class="text">Vegan</span>
                            <span class="hint">Keine tierischen Produkte</span>
                        </label>
                        <label class="radio-card ${d.diet_type === 'vegetarian' ? 'selected' : ''}">
                            <input type="radio" name="diet_type" value="vegetarian" ${d.diet_type === 'vegetarian' ? 'checked' : ''}>
                            <span class="icon">🥚</span>
                            <span class="text">Vegetarisch</span>
                            <span class="hint">Kein Fleisch, aber Milch & Eier</span>
                        </label>
                        <label class="radio-card ${d.diet_type === 'flexitarian' ? 'selected' : ''}">
                            <input type="radio" name="diet_type" value="flexitarian" ${d.diet_type === 'flexitarian' ? 'checked' : ''}>
                            <span class="icon">🥗</span>
                            <span class="text">Flexitarisch</span>
                            <span class="hint">Selten Fleisch (1-2x/Woche)</span>
                        </label>
                        <label class="radio-card ${d.diet_type === 'mixed' ? 'selected' : ''}">
                            <input type="radio" name="diet_type" value="mixed" ${d.diet_type === 'mixed' ? 'checked' : ''}>
                            <span class="icon">🍽️</span>
                            <span class="text">Mischkost</span>
                            <span class="hint">Regelmäßig Fleisch (3-5x/Woche)</span>
                        </label>
                        <label class="radio-card ${d.diet_type === 'meat_heavy' ? 'selected' : ''}">
                            <input type="radio" name="diet_type" value="meat_heavy" ${d.diet_type === 'meat_heavy' ? 'checked' : ''}>
                            <span class="icon">🥩</span>
                            <span class="text">Fleischlastig</span>
                            <span class="hint">Täglich Fleisch</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-group checkbox-group">
                    <label class="checkbox-card ${d.regional_seasonal ? 'selected' : ''}">
                        <input type="checkbox" name="regional_seasonal" ${d.regional_seasonal ? 'checked' : ''}>
                        <span class="icon">🌾</span>
                        <span class="text">Ich kaufe bevorzugt regional & saisonal</span>
                    </label>
                </div>
                
                <div class="form-group">
                    <label>Lebensmittelverschwendung</label>
                    <div class="radio-group small">
                        <label class="radio-card ${d.food_waste_level === 'low' ? 'selected' : ''}">
                            <input type="radio" name="food_waste_level" value="low" ${d.food_waste_level === 'low' ? 'checked' : ''}>
                            <span class="text">🌟 Wenig</span>
                        </label>
                        <label class="radio-card ${d.food_waste_level === 'medium' ? 'selected' : ''}">
                            <input type="radio" name="food_waste_level" value="medium" ${d.food_waste_level === 'medium' ? 'checked' : ''}>
                            <span class="text">📊 Mittel</span>
                        </label>
                        <label class="radio-card ${d.food_waste_level === 'high' ? 'selected' : ''}">
                            <input type="radio" name="food_waste_level" value="high" ${d.food_waste_level === 'high' ? 'checked' : ''}>
                            <span class="text">🗑️ Viel</span>
                        </label>
                    </div>
                </div>
            </div>
        `;
    }

    renderConsumptionStep() {
        const d = this.data.consumption;
        return `
            <div class="step-content">
                <h3>🛒 Konsum</h3>
                
                <div class="form-group">
                    <label>Wie oft kaufst du neue Dinge?</label>
                    <div class="radio-group vertical">
                        <label class="radio-card ${d.shopping_frequency === 'minimal' ? 'selected' : ''}">
                            <input type="radio" name="shopping_frequency" value="minimal" ${d.shopping_frequency === 'minimal' ? 'checked' : ''}>
                            <span class="icon">🎯</span>
                            <span class="text">Minimalistisch</span>
                            <span class="hint">Nur das Nötigste, sehr bewusst</span>
                        </label>
                        <label class="radio-card ${d.shopping_frequency === 'moderate' ? 'selected' : ''}">
                            <input type="radio" name="shopping_frequency" value="moderate" ${d.shopping_frequency === 'moderate' ? 'checked' : ''}>
                            <span class="icon">📦</span>
                            <span class="text">Durchschnittlich</span>
                            <span class="hint">Normal, gelegentlich Neues</span>
                        </label>
                        <label class="radio-card ${d.shopping_frequency === 'frequent' ? 'selected' : ''}">
                            <input type="radio" name="shopping_frequency" value="frequent" ${d.shopping_frequency === 'frequent' ? 'checked' : ''}>
                            <span class="icon">🛍️</span>
                            <span class="text">Häufig</span>
                            <span class="hint">Regelmäßig Shopping, Trends</span>
                        </label>
                    </div>
                </div>
                
                <div class="form-group checkbox-group">
                    <label class="checkbox-card ${d.secondhand_preference ? 'selected' : ''}">
                        <input type="checkbox" name="secondhand_preference" ${d.secondhand_preference ? 'checked' : ''}>
                        <span class="icon">♻️</span>
                        <span class="text">Ich kaufe gerne Secondhand</span>
                    </label>
                </div>
                
                <div class="form-group">
                    <label>Digitaler Konsum (Streaming, Gaming, etc.)</label>
                    <div class="radio-group small">
                        <label class="radio-card ${d.digital_consumption === 'low' ? 'selected' : ''}">
                            <input type="radio" name="digital_consumption" value="low" ${d.digital_consumption === 'low' ? 'checked' : ''}>
                            <span class="text">📱 Wenig</span>
                        </label>
                        <label class="radio-card ${d.digital_consumption === 'medium' ? 'selected' : ''}">
                            <input type="radio" name="digital_consumption" value="medium" ${d.digital_consumption === 'medium' ? 'checked' : ''}>
                            <span class="text">💻 Mittel</span>
                        </label>
                        <label class="radio-card ${d.digital_consumption === 'high' ? 'selected' : ''}">
                            <input type="radio" name="digital_consumption" value="high" ${d.digital_consumption === 'high' ? 'checked' : ''}>
                            <span class="text">🎮 Viel</span>
                        </label>
                    </div>
                </div>
            </div>
        `;
    }

    renderResultStep() {
        if (!this.result) {
            return `<div class="loading">Berechne deinen Fußabdruck...</div>`;
        }

        const r = this.result;
        const b = r.breakdown;
        const c = r.comparison;

        // Farbe basierend auf SEC-Score
        const scoreColor = r.sec_score >= 7 ? '#4caf50' : r.sec_score >= 4 ? '#ff9800' : '#f44336';

        return `
            <div class="step-content result-content">
                <div class="result-header">
                    <div class="total-footprint">
                        <span class="label">Dein CO₂-Fußabdruck</span>
                        <span class="value">${(r.total_co2_kg_year / 1000).toFixed(1)}</span>
                        <span class="unit">Tonnen/Jahr</span>
                    </div>
                    <div class="sec-score" style="--score-color: ${scoreColor}">
                        <span class="label">SEC-Score</span>
                        <span class="value">${r.sec_score}</span>
                        <span class="max">/10</span>
                    </div>
                </div>
                
                <div class="comparison-bars">
                    <div class="bar-item">
                        <span class="bar-label">Du</span>
                        <div class="bar-track">
                            <div class="bar-fill you" style="width: ${Math.min(100, r.total_co2_kg_year / 150)}%"></div>
                        </div>
                        <span class="bar-value">${(r.total_co2_kg_year / 1000).toFixed(1)}t</span>
                    </div>
                    <div class="bar-item">
                        <span class="bar-label">🇩🇪 Durchschnitt</span>
                        <div class="bar-track">
                            <div class="bar-fill germany" style="width: ${Math.min(100, c.germany_average_kg / 150)}%"></div>
                        </div>
                        <span class="bar-value">${(c.germany_average_kg / 1000).toFixed(1)}t</span>
                    </div>
                    <div class="bar-item">
                        <span class="bar-label">🌍 Welt</span>
                        <div class="bar-track">
                            <div class="bar-fill world" style="width: ${Math.min(100, c.world_average_kg / 150)}%"></div>
                        </div>
                        <span class="bar-value">${(c.world_average_kg / 1000).toFixed(1)}t</span>
                    </div>
                    <div class="bar-item">
                        <span class="bar-label">🎯 Paris-Ziel</span>
                        <div class="bar-track">
                            <div class="bar-fill target" style="width: ${Math.min(100, c.paris_target_kg / 150)}%"></div>
                        </div>
                        <span class="bar-value">${(c.paris_target_kg / 1000).toFixed(1)}t</span>
                    </div>
                </div>
                
                <div class="breakdown-chart">
                    <h4>Aufteilung</h4>
                    <div class="pie-chart">
                        <div class="pie-segment housing" style="--percentage: ${b.housing_percent}; --offset: 0"></div>
                        <div class="pie-segment mobility" style="--percentage: ${b.mobility_percent}; --offset: ${b.housing_percent}"></div>
                        <div class="pie-segment nutrition" style="--percentage: ${b.nutrition_percent}; --offset: ${b.housing_percent + b.mobility_percent}"></div>
                        <div class="pie-segment consumption" style="--percentage: ${b.consumption_percent}; --offset: ${b.housing_percent + b.mobility_percent + b.nutrition_percent}"></div>
                    </div>
                    <div class="pie-legend">
                        <div class="legend-item"><span class="dot housing"></span> Wohnen ${b.housing_percent}%</div>
                        <div class="legend-item"><span class="dot mobility"></span> Mobilität ${b.mobility_percent}%</div>
                        <div class="legend-item"><span class="dot nutrition"></span> Ernährung ${b.nutrition_percent}%</div>
                        <div class="legend-item"><span class="dot consumption"></span> Konsum ${b.consumption_percent}%</div>
                    </div>
                </div>
                
                <div class="recommendations">
                    <h4>💡 Top-Empfehlungen</h4>
                    ${r.recommendations.map(rec => `
                        <div class="rec-card">
                            <div class="rec-icon">${this.getCategoryIcon(rec.category)}</div>
                            <div class="rec-content">
                                <div class="rec-action">${rec.action}</div>
                                <div class="rec-savings">
                                    <span class="savings-value">-${Math.round(rec.potential_savings_kg)} kg</span>
                                    <span class="difficulty ${rec.difficulty}">${this.getDifficultyLabel(rec.difficulty)}</span>
                                </div>
                            </div>
                            ${rec.challenge_id ? `<button class="btn-join-challenge" data-challenge="${rec.challenge_id}">Challenge starten</button>` : ''}
                        </div>
                    `).join('')}
                </div>
                
                ${!this.isAuthenticated ? `
                    <div class="cta-register">
                        <p>🌱 <strong>Speichere dein Ergebnis!</strong> Registriere dich, um deinen Fortschritt zu tracken und Challenges zu starten.</p>
                        <button class="btn btn-primary" onclick="showAuthModal()">Jetzt registrieren</button>
                    </div>
                ` : `
                    <div class="cta-saved">
                        <p>✅ Dein Fußabdruck wurde gespeichert! Challenge ON-1 "Klimaheld-Profil" abgeschlossen. +50 XP</p>
                    </div>
                `}
            </div>
        `;
    }

    getCategoryIcon(category) {
        const icons = { housing: '🏠', mobility: '🚗', nutrition: '🥗', consumption: '🛒' };
        return icons[category] || '💡';
    }

    getDifficultyLabel(difficulty) {
        const labels = { easy: '⭐ Einfach', medium: '⭐⭐ Mittel', hard: '⭐⭐⭐ Schwer' };
        return labels[difficulty] || difficulty;
    }

    renderNavigation() {
        const isFirst = this.currentStep === 0;
        const isLast = this.currentStep === this.steps.length - 1;
        const isBeforeResult = this.currentStep === this.steps.length - 2;

        return `
            <button class="btn btn-secondary" ${isFirst ? 'disabled' : ''} onclick="footprintCalc.prevStep()">
                ← Zurück
            </button>
            ${isLast ? `
                <button class="btn btn-primary" onclick="footprintCalc.restart()">
                    🔄 Neu berechnen
                </button>
            ` : `
                <button class="btn btn-primary" onclick="footprintCalc.nextStep()">
                    ${isBeforeResult ? '📊 Berechnen' : 'Weiter →'}
                </button>
            `}
        `;
    }

    attachEventListeners() {
        // Radio buttons
        this.container.querySelectorAll('input[type="radio"]').forEach(input => {
            input.addEventListener('change', (e) => this.updateValue(e.target.name, e.target.value));
        });

        // Checkboxes
        this.container.querySelectorAll('input[type="checkbox"]').forEach(input => {
            input.addEventListener('change', (e) => this.updateValue(e.target.name, e.target.checked));
        });

        // Sliders
        this.container.querySelectorAll('input[type="range"]').forEach(input => {
            input.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                this.updateValue(e.target.name, value);
                const display = e.target.nextElementSibling;
                if (display && display.classList.contains('slider-value')) {
                    if (e.target.name.includes('km')) {
                        display.textContent = value.toLocaleString('de') + ' km' + (e.target.name === 'bike_km_year' ? ' 🚲' : '');
                    } else if (e.target.name.includes('sqm')) {
                        display.textContent = value + ' m²';
                    } else if (e.target.name.includes('flights')) {
                        display.textContent = value + ' Flüge/Jahr';
                    } else {
                        display.textContent = value;
                    }
                }
            });
        });

        // Selects
        this.container.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', (e) => this.updateValue(e.target.name, e.target.value));
        });

        // Car toggle
        const hasCarCheckbox = this.container.querySelector('input[name="has_car"]');
        if (hasCarCheckbox) {
            hasCarCheckbox.addEventListener('change', () => {
                const carDetails = this.container.querySelector('.car-details');
                if (carDetails) {
                    carDetails.classList.toggle('hidden', !this.data.mobility.has_car);
                }
            });
        }

        // Challenge join buttons
        this.container.querySelectorAll('.btn-join-challenge').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const challengeId = e.target.dataset.challenge;
                if (this.isAuthenticated) {
                    this.joinChallenge(challengeId);
                } else {
                    showAuthModal();
                }
            });
        });
    }

    updateValue(name, value) {
        // Find which category this field belongs to
        for (const category of ['housing', 'mobility', 'nutrition', 'consumption']) {
            if (name in this.data[category]) {
                this.data[category][name] = value;
                break;
            }
        }

        // Update UI for radio/checkbox cards
        const cards = this.container.querySelectorAll(`input[name="${name}"]`);
        cards.forEach(input => {
            const card = input.closest('.radio-card, .checkbox-card');
            if (card) {
                card.classList.toggle('selected', input.checked);
            }
        });
    }

    async nextStep() {
        if (this.currentStep < this.steps.length - 1) {
            this.currentStep++;

            // If moving to result step, calculate
            if (this.steps[this.currentStep] === 'result') {
                await this.calculate();
            }

            this.render();
        }
    }

    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.render();
        }
    }

    async calculate() {
        try {
            // Use authenticated endpoint if logged in
            const endpoint = this.isAuthenticated ? '/footprint/me' : '/footprint/calculate';

            // Debug logging
            const token = this.api?.getToken?.() || null;
            console.log('[Footprint] Calculating...', {
                isAuthenticated: this.isAuthenticated,
                hasApiClient: !!this.api,
                hasToken: !!token,
                endpoint
            });

            // Use API client's footprint methods if available
            if (this.api && this.isAuthenticated && typeof this.api.footprint?.save === 'function') {
                console.log('[Footprint] Using api.footprint.save()');
                this.result = await this.api.footprint.save(this.data);
            } else if (this.api && typeof this.api.footprint?.calculate === 'function') {
                console.log('[Footprint] Using api.footprint.calculate()');
                this.result = await this.api.footprint.calculate(this.data);
            } else {
                // Fallback: Use global API_BASE_URL from config.js
                console.log('[Footprint] Using fallback fetch');
                const baseUrl = window.API_BASE_URL || 'https://provolution-api.onrender.com/v1';
                const response = await fetch(`${baseUrl}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(this.isAuthenticated && token ? { 'Authorization': `Bearer ${token}` } : {})
                    },
                    body: JSON.stringify(this.data)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || 'Calculation failed');
                }

                this.result = await response.json();
            }

            console.log('[Footprint] Calculation result:', this.result);

            // Auto-complete ON-1 challenge for authenticated users
            if (this.isAuthenticated) {
                await this.autoCompleteOnboardingChallenge();
            }
        } catch (error) {
            console.error('Footprint calculation error:', error);
            alert('Fehler bei der Berechnung: ' + error.message);
        }
    }

    /**
     * Auto-complete the ON-1 "Klimaheld-Profil" challenge after first footprint calculation
     */
    async autoCompleteOnboardingChallenge() {
        const ON1_CHALLENGE_ID = 'ON-1';

        try {
            // Check if challengesUI is available
            if (!window.challengesUI) {
                console.log('[Footprint] ChallengesUI not available, skipping ON-1 auto-complete');
                return;
            }

            // Find ON-1 challenge
            const on1Challenge = window.challengesUI.challenges.find(c =>
                c.id === ON1_CHALLENGE_ID || c.id?.toLowerCase() === 'on-1'
            );

            if (!on1Challenge) {
                console.log('[Footprint] ON-1 challenge not found');
                return;
            }

            // Check if already completed
            if (on1Challenge.user_status === 'completed') {
                console.log('[Footprint] ON-1 already completed');
                return;
            }

            // If not joined, join first
            if (on1Challenge.user_status !== 'active') {
                console.log('[Footprint] Joining ON-1 challenge first...');
                try {
                    await ProvolutionAPI.challenges.join(ON1_CHALLENGE_ID);
                } catch (err) {
                    // Might already be joined, continue
                    console.log('[Footprint] Join attempt:', err.message);
                }
            }

            // Complete the challenge
            console.log('[Footprint] Auto-completing ON-1 challenge...');
            const result = await ProvolutionAPI.challenges.complete(ON1_CHALLENGE_ID);

            // Update local state
            on1Challenge.user_status = 'completed';

            // Show celebration via challengesUI
            if (window.challengesUI?.showCompletionCelebration) {
                window.challengesUI.showCompletionCelebration(on1Challenge, result);
            } else {
                // Fallback notification
                this.showOnboardingCompleteNotification(result?.xp_earned || 50);
            }

            // Reload challenges UI if available
            if (window.challengesUI?.loadActiveChallenges) {
                await window.challengesUI.loadActiveChallenges();
                await window.challengesUI.loadChallenges();
            }

            // Emit XP event
            window.dispatchEvent(new CustomEvent('xp:earned', {
                detail: { xp: result?.xp_earned || 50, challengeId: ON1_CHALLENGE_ID, challengeName: on1Challenge.name }
            }));

            console.log('[Footprint] ON-1 challenge completed successfully!');
        } catch (error) {
            console.error('[Footprint] ON-1 auto-complete error:', error);
            // Don't show error to user, this is a bonus feature
        }
    }

    showOnboardingCompleteNotification(xpEarned) {
        const notification = document.createElement('div');
        notification.className = 'notification notification-success';
        notification.innerHTML = `🎉 Challenge ON-1 abgeschlossen! +${xpEarned} XP`;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    restart() {
        this.currentStep = 0;
        this.data = this.getDefaultData();
        this.result = null;
        this.render();
    }

    async joinChallenge(challengeId) {
        // Delegate to challenges UI
        if (window.challengesUI && typeof window.challengesUI.joinChallenge === 'function') {
            await window.challengesUI.joinChallenge(challengeId);
        }
    }
}

// Global instance
let footprintCalc;

function initFootprintCalculator(containerId, apiClient, isAuthenticated) {
    footprintCalc = new FootprintCalculator(containerId, apiClient);
    footprintCalc.init(isAuthenticated);
    return footprintCalc;
}
