// --- API Base URL Configuration ---
const API_BASE = '/api';

// --- State Management ---
let appState = {
    lastAnalysis: null,
    totalProducts: 0,
    totalChemicals: 0
};

// --- Preset Ingredient Lists for Demos ---
const DEMO_LABELS = {
    bread: {
        name: "Atta Sandwich Bread",
        brand: "Britannia Premium",
        category: "Food",
        ingredients: "Wheat Flour (Atta 60%), Maida, Sugar, Yeast, Iodized Salt, Preservative (Sodium Benzoate E211), Flour Treatment Agent (Potassium Bromate E924), Gluten, Soya Flour, Water, Calcium Propionate"
    },
    cream: {
        name: "Daily Brightness Glow Cream",
        brand: "Fair Glow",
        category: "Cosmetics",
        ingredients: "Water, Palmitic Acid, Stearic Acid, Niacinamide, Glycerin, Preservative (Isopropylparaben), Isobutylparaben, Methylparaben, Perfume, Titanium Dioxide, Disodium EDTA, Triclosan (0.3%)"
    },
    safe: {
        name: "Natural Almond Honey Oats Muesli",
        brand: "Organic Harvest",
        category: "Food",
        ingredients: "Whole Grain Oats, Rolled Oats, Almonds, Honey, Chia Seeds, Real Vanilla Extract, Raisins, Pumpkin Seeds, Flax Seeds"
    }
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    setupRouter();
    setupForms();
    setupPresets();
    setupSearchFilters();
    loadDashboardStats();
    loadProducts();
    loadChemicals();
    
    // Initialise Lucide icons
    lucide.createIcons();
});

// --- Toast Notification Helper ---
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-message');
    
    toast.className = `toast show ${type}`;
    toastMsg.textContent = message;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 4000);
}

// --- Router / View Swapper ---
function setupRouter() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            const target = item.getAttribute('data-target');
            
            // Remove active classes
            navItems.forEach(i => i.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // Set active class
            item.classList.add('active');
            const targetSection = document.getElementById(target);
            if (targetSection) {
                targetSection.classList.add('active');
            }
            
            // Refresh content if switching pages
            if (target === 'dashboard') loadDashboardStats();
            if (target === 'products') loadProducts();
            if (target === 'chemicals') loadChemicals();
            
            // Render icons for dynamically switched views
            lucide.createIcons();
        });
    });
}

// --- Dashboard Loader ---
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE}/dashboard-stats`);
        if (!response.ok) throw new Error("Failed to load dashboard metrics");
        
        const data = await response.json();
        
        // Populate stats
        document.getElementById('stat-total-products').textContent = data.total_products;
        document.getElementById('stat-total-chemicals').textContent = data.total_chemicals;
        document.getElementById('stat-avg-score').textContent = data.average_risk_score;
        
        // Mini stats in admin
        document.getElementById('mini-stat-food').textContent = data.chemical_risk_breakdown.high + data.chemical_risk_breakdown.medium;
        document.getElementById('mini-stat-cosmetic').textContent = data.chemical_risk_breakdown.medium + data.chemical_risk_breakdown.low;
        document.getElementById('mini-stat-user').textContent = data.total_products;

        // Safety grading and styling
        const avgScore = data.average_risk_score;
        const avgGradeSpan = document.getElementById('stat-avg-grade');
        const avgIcon = document.getElementById('stat-safety-icon');
        
        let gradeText = "Grade A";
        let gradeClass = "grade-a";
        let iconClass = "green";
        
        if (avgScore >= 81) {
            gradeText = "Grade A (Excellent)";
            gradeClass = "grade-a";
            iconClass = "risk-safe";
        } else if (avgScore >= 61) {
            gradeText = "Grade B (Good)";
            gradeClass = "grade-b";
            iconClass = "primary";
        } else if (avgScore >= 41) {
            gradeText = "Grade C (Caution)";
            gradeClass = "grade-c";
            iconClass = "risk-low";
        } else if (avgScore >= 21) {
            gradeText = "Grade D (Warning)";
            gradeClass = "grade-d";
            iconClass = "risk-med";
        } else {
            gradeText = "Grade F (Hazardous)";
            gradeClass = "grade-f";
            iconClass = "risk-high";
        }
        
        avgGradeSpan.textContent = gradeText;
        avgGradeSpan.className = `metric-sub safety-badge ${gradeClass}`;
        
        // Apply color to icon container
        avgIcon.className = `metric-icon`;
        avgIcon.style.color = `var(--${iconClass})`;
        avgIcon.style.backgroundColor = `rgba(var(--${iconClass}-glow), 0.1)`;

        // Render Recent Table
        const recentTable = document.getElementById('recent-scans-table');
        if (data.recent_scans && data.recent_scans.length > 0) {
            recentTable.innerHTML = data.recent_scans.map(prod => `
                <tr>
                    <td><strong>${escapeHtml(prod.name)}</strong></td>
                    <td>${escapeHtml(prod.brand || 'Generic')}</td>
                    <td><span class="category-tag">${escapeHtml(prod.category)}</span></td>
                    <td><span class="safety-badge ${getGradeClass(prod.risk_score)}">${prod.risk_score} (${getGradeText(prod.risk_score)})</span></td>
                    <td>
                        <button class="btn-delete" onclick="deleteProduct(${prod.id}, 'dashboard')" title="Delete Scan">
                            <i data-lucide="trash-2"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        } else {
            recentTable.innerHTML = `<tr><td colspan="5" class="empty-state">No products scanned yet. Go to Scan Ingredients!</td></tr>`;
        }

        // Render High Risk Flags
        const flagList = document.getElementById('high-risk-list');
        if (data.high_risk_products && data.high_risk_products.length > 0) {
            flagList.innerHTML = data.high_risk_products.map(prod => `
                <div class="flagged-item">
                    <div class="flagged-info">
                        <h4>${escapeHtml(prod.name)}</h4>
                        <span>${escapeHtml(prod.brand || 'Generic')} • ${escapeHtml(prod.category)}</span>
                    </div>
                    <div class="flagged-score">${prod.risk_score}</div>
                </div>
            `).join('');
        } else {
            flagList.innerHTML = `<div class="empty-state">No high-risk products found. All clear!</div>`;
        }
        
        lucide.createIcons();

    } catch (err) {
        console.error(err);
        showToast(err.message, 'error');
    }
}

// --- Presets loader ---
function setupPresets() {
    const buttons = document.querySelectorAll('.btn-preset');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.getAttribute('data-type');
            const data = DEMO_LABELS[type];
            if (data) {
                document.getElementById('scan-name').value = data.name;
                document.getElementById('scan-brand').value = data.brand;
                document.getElementById('scan-category').value = data.category;
                document.getElementById('scan-ingredients').value = data.ingredients;
                showToast(`Loaded preset demo ingredients for ${data.name}!`);
            }
        });
    });
}

// --- Scan & Analyze Core Logic ---
function setupForms() {
    const scanForm = document.getElementById('scan-form');
    const resetScanBtn = document.getElementById('btn-reset-scan');
    const saveProductBtn = document.getElementById('btn-save-product');
    
    // Reset Form & Results UI
    resetScanBtn.addEventListener('click', () => {
        scanForm.reset();
        document.getElementById('results-card').style.display = 'none';
        document.getElementById('results-empty-state').style.display = 'flex';
        appState.lastAnalysis = null;
        showToast("Scan interface cleared.");
    });
    
    // Save analyzed product to DB
    saveProductBtn.addEventListener('click', async () => {
        if (!appState.lastAnalysis) return;
        
        try {
            const body = {
                name: appState.lastAnalysis.product_name || "Unnamed Scan",
                brand: appState.lastAnalysis.brand || "Generic",
                category: appState.lastAnalysis.category,
                ingredients_text: appState.lastAnalysis.ingredients_text
            };
            
            const response = await fetch(`${API_BASE}/products`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            if (!response.ok) throw new Error("Failed to save product to directory");
            
            showToast("Product successfully saved to directory!");
            saveProductBtn.disabled = true;
            saveProductBtn.innerHTML = `<i data-lucide="check"></i> Saved in Directory`;
            lucide.createIcons();
            
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    // Run ingredient risk scanner
    scanForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('scan-name').value.stripOrEmpty();
        const brand = document.getElementById('scan-brand').value.stripOrEmpty();
        const category = document.getElementById('scan-category').value;
        const ingredientsText = document.getElementById('scan-ingredients').value;
        
        const btnSubmit = document.getElementById('btn-submit-scan');
        const origBtnHtml = btnSubmit.innerHTML;
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = `<i data-lucide="loader" class="spin"></i> Analyzing...`;
        lucide.createIcons();
        
        try {
            const response = await fetch(`${API_BASE}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name || null,
                    brand: brand || null,
                    category: category,
                    ingredients_text: ingredientsText
                })
            });
            
            if (!response.ok) throw new Error("Server analysis failed. Please verify syntax.");
            
            const data = await response.json();
            
            // Save in temporary state
            appState.lastAnalysis = {
                ...data,
                ingredients_text: ingredientsText
            };
            
            // Toggle results view
            document.getElementById('results-empty-state').style.display = 'none';
            const resultsCard = document.getElementById('results-card');
            resultsCard.style.display = 'flex';
            
            // Enable Save button
            saveProductBtn.disabled = false;
            saveProductBtn.innerHTML = `<i data-lucide="save"></i> Save Scan to Directory`;
            
            // Populate results
            document.getElementById('result-product-title').textContent = data.product_name || "Unnamed Product Scan";
            document.getElementById('result-product-meta').textContent = `${data.brand || 'Generic'} • ${data.category}`;
            
            // Grade and colors
            const gradeBadge = document.getElementById('result-grade');
            gradeBadge.textContent = data.grade;
            gradeBadge.className = `grade-badge safety-badge ${getGradeClassByLetter(data.grade)}`;
            
            // Safety Gauge
            const scoreText = document.getElementById('result-score-text');
            const scoreFill = document.getElementById('result-gauge-fill');
            scoreText.textContent = data.risk_score;
            
            // Calculate SVG dashoffset (circumference of r=40 is ~251)
            const circumference = 251;
            const offset = circumference - (circumference * data.risk_score) / 100;
            scoreFill.style.strokeDashoffset = offset;
            
            // Color of gauge line based on grade
            scoreFill.style.stroke = getGradeColor(data.risk_score);
            
            // Summary and description
            document.getElementById('result-summary-title').textContent = getGradeSummaryTitle(data.risk_score);
            document.getElementById('result-summary-desc').textContent = data.summary;
            
            // Strip counts
            document.getElementById('count-high').textContent = data.high_risk_count;
            document.getElementById('count-med').textContent = data.medium_risk_count;
            document.getElementById('count-low').textContent = data.low_risk_count;
            
            // Matched Dangerous Chemicals List
            const matchedContainer = document.getElementById('matched-chemicals-list');
            const matchedSection = document.getElementById('matched-chemicals-section');
            
            if (data.matched_ingredients && data.matched_ingredients.length > 0) {
                matchedSection.style.display = 'block';
                matchedContainer.innerHTML = data.matched_ingredients.map(match => {
                    const chem = match.matched_chemical;
                    const statusClass = chem.regulatory_status.toLowerCase() === 'prohibited' ? 'prohibited' : 'restricted';
                    
                    return `
                        <div class="matched-chem-card">
                            <div class="matched-chem-header">
                                <h5>${escapeHtml(chem.name)}</h5>
                                <span class="status-badge ${statusClass}">${escapeHtml(chem.regulatory_status)}</span>
                            </div>
                            <div class="matched-chem-meta">
                                <span>Risk: <strong style="color: ${getRiskColor(chem.risk_level)}">${escapeHtml(chem.risk_level)}</strong></span>
                                <span>Code/Syn: <strong>${escapeHtml(chem.synonyms || 'None')}</strong></span>
                                <span>Authority: <strong>${escapeHtml(chem.regulatory_body)}</strong></span>
                            </div>
                            <div class="matched-chem-hazards">
                                <strong>Hazards:</strong> ${escapeHtml(chem.health_risks || 'No details reported.')}
                            </div>
                            <div class="matched-chem-desc">
                                ${escapeHtml(chem.description || 'No description.')} 
                                ${chem.regulatory_limit ? `<br><strong>Regulatory Limit:</strong> ${escapeHtml(chem.regulatory_limit)}` : ''}
                            </div>
                            ${chem.source_url ? `
                                <a href="${escapeHtml(chem.source_url)}" target="_blank" class="matched-chem-source">
                                    <i data-lucide="external-link" style="width:12px;height:12px;"></i> View Gazette / Notification
                                </a>
                            ` : ''}
                        </div>
                    `;
                }).join('');
            } else {
                matchedSection.style.display = 'none';
                matchedContainer.innerHTML = '';
            }
            
            // Unmatched Clean Ingredients
            const unmatchedContainer = document.getElementById('unmatched-ingredients-list');
            if (data.unmatched_ingredients && data.unmatched_ingredients.length > 0) {
                unmatchedContainer.innerHTML = data.unmatched_ingredients.map(ing => `
                    <span class="ing-tag">${escapeHtml(ing)}</span>
                `).join('');
            } else {
                unmatchedContainer.innerHTML = '<span class="empty-state" style="padding:0;">None</span>';
            }
            
            showToast("Analysis complete!");
            lucide.createIcons();
            
        } catch (err) {
            console.error(err);
            showToast(err.message, 'error');
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = origBtnHtml;
            lucide.createIcons();
        }
    });

    // Admin - Create chemical form submit handler
    const addChemForm = document.getElementById('add-chemical-form');
    addChemForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const body = {
            name: document.getElementById('chem-name').value.trim(),
            cas_number: document.getElementById('chem-cas').value.trim() || null,
            category: document.getElementById('chem-category').value,
            regulatory_status: document.getElementById('chem-status').value,
            regulatory_body: document.getElementById('chem-body').value,
            risk_level: document.getElementById('chem-risk').value,
            regulatory_limit: document.getElementById('chem-limit').value.trim() || null,
            synonyms: document.getElementById('chem-synonyms').value.trim() || null,
            health_risks: document.getElementById('chem-hazards').value.trim(),
            description: document.getElementById('chem-description').value.trim(),
            source_url: document.getElementById('chem-source').value.trim() || null
        };
        
        try {
            const response = await fetch(`${API_BASE}/chemicals`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Failed to add chemical rule.");
            }
            
            showToast("New chemical regulation rule successfully registered!");
            addChemForm.reset();
            loadChemicals();
            loadDashboardStats();
            
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    // Admin - Re-seed Database
    const dbSeedBtn = document.getElementById('btn-db-seed');
    dbSeedBtn.addEventListener('click', async () => {
        const confirmReset = confirm("Are you absolutely sure you want to wipe the database and re-seed defaults? Any customized data will be lost.");
        if (!confirmReset) return;
        
        const origBtnText = dbSeedBtn.innerHTML;
        dbSeedBtn.disabled = true;
        dbSeedBtn.innerHTML = `<i data-lucide="loader" class="spin"></i> Re-seeding...`;
        lucide.createIcons();
        
        try {
            const response = await fetch(`${API_BASE}/admin/seed-reset`, {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error("Failed to re-seed chemical database");
            
            showToast("Database successfully cleaned and seeded with FSSAI/CDSCO rules!");
            loadDashboardStats();
            loadProducts();
            loadChemicals();
            
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            dbSeedBtn.disabled = false;
            dbSeedBtn.innerHTML = origBtnText;
            lucide.createIcons();
        }
    });
}

// --- Product Directory Loader & Filters ---
async function loadProducts(search = '', category = 'All') {
    const grid = document.getElementById('product-list-grid');
    grid.innerHTML = `<div class="empty-state"><i data-lucide="loader" class="spin" style="width:30px;height:30px;margin-bottom:10px;"></i><br>Loading products...</div>`;
    lucide.createIcons();
    
    try {
        let url = `${API_BASE}/products`;
        const params = [];
        if (search) params.push(`search=${encodeURIComponent(search)}`);
        if (category && category !== 'All') params.push(`category=${encodeURIComponent(category)}`);
        if (params.length > 0) url += `?${params.join('&')}`;
        
        const response = await fetch(url);
        if (!response.ok) throw new Error("Failed to load products");
        
        const products = await response.json();
        
        if (products.length === 0) {
            grid.innerHTML = `<div class="empty-state">No matching scanned products found. Try typing another search keyword.</div>`;
            return;
        }
        
        grid.innerHTML = products.map(prod => `
            <div class="product-card glass">
                <div class="product-card-top">
                    <div class="product-card-header">
                        <h4>${escapeHtml(prod.name)}</h4>
                        <span class="safety-badge ${getGradeClass(prod.risk_score)}">${prod.risk_score} (${getGradeText(prod.risk_score)})</span>
                    </div>
                    <div class="product-card-brand">Brand: <strong>${escapeHtml(prod.brand || 'Generic')}</strong></div>
                    <div class="chem-info-row" style="font-size: 0.8rem; line-height: 1.4; color: var(--text-secondary); margin-bottom: 12px;">
                        <strong>Ingredients:</strong> <span class="chem-info-desc">${escapeHtml(truncateString(prod.ingredients_text, 140))}</span>
                    </div>
                </div>
                <div class="product-card-actions">
                    <div class="product-card-meta">
                        <span>Category: ${escapeHtml(prod.category)}</span>
                    </div>
                    <button class="btn-delete" onclick="deleteProduct(${prod.id}, 'directory')" title="Delete Product">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </div>
        `).join('');
        
        lucide.createIcons();
        
    } catch (err) {
        console.error(err);
        grid.innerHTML = `<div class="empty-state error" style="color:var(--risk-high);">${err.message}</div>`;
    }
}

// Delete Product Action
async function deleteProduct(id, origin = 'directory') {
    const confirmDelete = confirm("Are you sure you want to delete this scan history?");
    if (!confirmDelete) return;
    
    try {
        const response = await fetch(`${API_BASE}/products/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error("Failed to delete product");
        
        showToast("Product deleted successfully");
        if (origin === 'directory') {
            loadProducts(
                document.getElementById('product-search-input').value,
                document.getElementById('product-category-filter').value
            );
        } else {
            loadDashboardStats();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// --- Chemical Registry Loader ---
async function loadChemicals(search = '') {
    const grid = document.getElementById('chemical-registry-list');
    grid.innerHTML = `<div class="empty-state"><i data-lucide="loader" class="spin" style="width:30px;height:30px;margin-bottom:10px;"></i><br>Loading chemicals...</div>`;
    lucide.createIcons();
    
    try {
        let url = `${API_BASE}/chemicals`;
        if (search) url += `?search=${encodeURIComponent(search)}`;
        
        const response = await fetch(url);
        if (!response.ok) throw new Error("Failed to fetch chemicals list");
        
        const chemicals = await response.json();
        
        if (chemicals.length === 0) {
            grid.innerHTML = `<div class="empty-state">No matching chemicals found in FSSAI / CDSCO database.</div>`;
            return;
        }
        
        grid.innerHTML = chemicals.map(chem => {
            const statusClass = chem.regulatory_status.toLowerCase() === 'prohibited' ? 'prohibited' : 'restricted';
            return `
                <div class="chemical-card glass">
                    <div>
                        <div class="chemical-card-header">
                            <div class="chemical-card-title">
                                <h4>${escapeHtml(chem.name)}</h4>
                                <span>CAS Number: ${escapeHtml(chem.cas_number || 'N/A')}</span>
                            </div>
                            <span class="status-badge ${statusClass}">${escapeHtml(chem.regulatory_status)}</span>
                        </div>
                        <div class="chemical-card-body">
                            <div class="chem-info-row">
                                <strong>Authority:</strong> <span class="chem-info-desc">${escapeHtml(chem.regulatory_body)}</span>
                            </div>
                            <div class="chem-info-row">
                                <strong>Applicability:</strong> <span class="chem-info-desc">${escapeHtml(chem.category)} Additive</span>
                            </div>
                            ${chem.regulatory_limit ? `
                                <div class="chem-info-row">
                                    <strong>Max Limit:</strong> <span class="chem-info-desc">${escapeHtml(chem.regulatory_limit)}</span>
                                </div>
                            ` : ''}
                            <div class="chem-info-row">
                                <strong>Synonyms:</strong> <span class="chem-info-desc">${escapeHtml(chem.synonyms || 'None')}</span>
                            </div>
                            <div class="chem-card-health">
                                <strong>Side Effects:</strong> ${escapeHtml(chem.health_risks || 'No details.')}
                            </div>
                            <div class="chem-info-row" style="margin-top:6px;">
                                <strong>Description:</strong> <span class="chem-info-desc">${escapeHtml(chem.description || 'No description.')}</span>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.04); padding-top:12px; margin-top:auto;">
                        <span style="font-size:0.75rem; color:var(--text-muted);">Risk Rating: <strong style="color: ${getRiskColor(chem.risk_level)}">${escapeHtml(chem.risk_level)}</strong></span>
                        <div style="display:flex; gap:10px; align-items:center;">
                            ${chem.source_url ? `
                                <a href="${escapeHtml(chem.source_url)}" target="_blank" class="matched-chem-source" style="margin-top:0;">
                                    <i data-lucide="external-link" style="width:12px;height:12px;"></i> Gazette
                                </a>
                            ` : ''}
                            <!-- Admin Delete Rule -->
                            <button class="btn-delete" onclick="deleteChemicalRule(${chem.id})" title="Delete Regulation Rule" style="width:24px;height:24px;">
                                <i data-lucide="trash-2" style="width:12px;height:12px;"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        lucide.createIcons();
        
    } catch (err) {
        console.error(err);
        grid.innerHTML = `<div class="empty-state error" style="color:var(--risk-high);">${err.message}</div>`;
    }
}

// Delete Chemical Rule Action
async function deleteChemicalRule(id) {
    const confirmDelete = confirm("Are you sure you want to permanently delete this regulation rule from the registry?");
    if (!confirmDelete) return;
    
    try {
        const response = await fetch(`${API_BASE}/chemicals/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error("Failed to delete chemical regulation rule");
        
        showToast("Regulation rule deleted successfully");
        loadChemicals(document.getElementById('chemical-search-input').value);
        loadDashboardStats();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// --- Search and Filters Debounces ---
function setupSearchFilters() {
    // Product list filters
    const prodSearch = document.getElementById('product-search-input');
    const prodCat = document.getElementById('product-category-filter');
    
    const triggerProdFilter = () => {
        loadProducts(prodSearch.value, prodCat.value);
    };
    
    prodSearch.addEventListener('input', debounce(triggerProdFilter, 300));
    prodCat.addEventListener('change', triggerProdFilter);
    
    // Chemical list filters
    const chemSearch = document.getElementById('chemical-search-input');
    chemSearch.addEventListener('input', debounce(() => {
        loadChemicals(chemSearch.value);
    }, 300));
}

// --- Helper Functions ---

// Debounce helper
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Truncate string helper
function truncateString(str, num) {
    if (!str) return '';
    if (str.length <= num) return str;
    return str.slice(0, num) + '...';
}

// Escape HTML entities to prevent XSS injection
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function (m) { return map[m]; });
}

// Strip whitespace and check if empty
String.prototype.stripOrEmpty = function() {
    return this.trim();
};

// Map score to grade letter classes
function getGradeClass(score) {
    if (score >= 81) return 'grade-a';
    if (score >= 61) return 'grade-b';
    if (score >= 41) return 'grade-c';
    if (score >= 21) return 'grade-d';
    return 'grade-f';
}

function getGradeClassByLetter(grade) {
    return `grade-${grade.toLowerCase()}`;
}

// Map score to Grade summary title
function getGradeSummaryTitle(score) {
    if (score >= 81) return 'Safe Product Profile';
    if (score >= 61) return 'Satisfactory Profile';
    if (score >= 41) return 'Caution Suggested';
    if (score >= 21) return 'Warning: Restricted Ingredients';
    return 'Dangerous Product: Banned Additives';
}

// Map score to grade letters
function getGradeText(score) {
    if (score >= 81) return 'A';
    if (score >= 61) return 'B';
    if (score >= 41) return 'C';
    if (score >= 21) return 'D';
    return 'F';
}

// Get safety color representation
function getGradeColor(score) {
    if (score >= 81) return 'var(--risk-safe)';
    if (score >= 61) return '#34d399';
    if (score >= 41) return 'var(--risk-low)';
    if (score >= 21) return 'var(--risk-med)';
    return 'var(--risk-high)';
}

// Map chemical risk level string to CSS color codes
function getRiskColor(riskLevel) {
    const lvl = riskLevel.toLowerCase();
    if (lvl === 'high') return 'var(--risk-high)';
    if (lvl === 'medium') return 'var(--risk-med)';
    if (lvl === 'low') return 'var(--risk-low)';
    return 'var(--risk-safe)';
}

// Globally bind delete handlers so inline HTML onclicks can call them
window.deleteProduct = deleteProduct;
window.deleteChemicalRule = deleteChemicalRule;
