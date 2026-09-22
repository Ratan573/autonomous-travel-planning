/**
 * Main Application Logic for LangGraph Travel Planner
 */

document.addEventListener("DOMContentLoaded", () => {
    // State
    let currentPlan = null;
    let mapManager = null;
    let streamClient = null;

    // DOM Elements
    const form = document.getElementById("travelPlanForm");
    const generateBtn = document.getElementById("generatePlanBtn");
    const btnSpinner = document.getElementById("btnSpinner");
    const btnText = document.getElementById("btnText");
    const durationRange = document.getElementById("durationDays");
    const durationVal = document.getElementById("durationVal");
    const emptyState = document.getElementById("emptyPlanState");
    const planContainer = document.getElementById("planContentContainer");
    const thoughtConsole = document.getElementById("agentThoughtConsole");
    const thoughtLogsList = document.getElementById("thoughtLogsList");
    const toggleLogsBtn = document.getElementById("toggleLogsBtn");
    const logToggleLabel = document.getElementById("logToggleLabel");
    const clearLogsBtn = document.getElementById("clearLogsBtn");
    const savedCountBadge = document.getElementById("savedCountBadge");

    // Modals
    const savedModal = document.getElementById("savedPlansModal");
    const archModal = document.getElementById("architectureModal");
    const settingsModal = document.getElementById("settingsModal");

    // Initialize Map Manager
    mapManager = new TravelMapManager("travelMap");

    // 1. Duration Slider Update
    durationRange.addEventListener("input", (e) => {
        durationVal.textContent = `${e.target.value} Day${e.target.value > 1 ? 's' : ''}`;
    });

    // 2. Budget Selection Visuals
    document.querySelectorAll(".budget-card input").forEach(input => {
        input.addEventListener("change", (e) => {
            document.querySelectorAll(".budget-card").forEach(c => c.classList.remove("selected"));
            e.target.closest(".budget-card").classList.add("selected");
        });
    });

    // 3. Interest Chips Toggle
    document.querySelectorAll(".interest-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const checkbox = chip.querySelector("input");
            checkbox.checked = !checkbox.checked;
            chip.classList.toggle("active", checkbox.checked);
        });
    });

    // 4. Preset Chips
    document.querySelectorAll(".chip-preset").forEach(btn => {
        btn.addEventListener("click", () => {
            document.getElementById("destinationInput").value = btn.dataset.dest;
            document.getElementById("originInput").value = btn.dataset.origin;
            durationRange.value = btn.dataset.days;
            durationVal.textContent = `${btn.dataset.days} Days`;
            document.getElementById("travelStyle").value = btn.dataset.style;

            // Budget
            const budgetTier = btn.dataset.budget;
            const targetRadio = document.querySelector(`input[name="budgetTier"][value="${budgetTier}"]`);
            if (targetRadio) {
                targetRadio.checked = true;
                document.querySelectorAll(".budget-card").forEach(c => c.classList.remove("selected"));
                targetRadio.closest(".budget-card").classList.add("selected");
            }
        });
    });

    // 5. Thought Console Toggle
    toggleLogsBtn.addEventListener("click", () => {
        const isVisible = thoughtConsole.classList.toggle("visible");
        logToggleLabel.textContent = isVisible ? "Hide Agent Thought Stream" : "Show Agent Thought Stream";
    });

    clearLogsBtn.addEventListener("click", () => {
        thoughtLogsList.innerHTML = `
            <div class="log-line log-system">
                <span class="log-time">[System]</span>
                <span class="log-msg">Logs cleared. Ready for next multi-agent run.</span>
            </div>
        `;
    });

    // 6. Navigation Tabs
    document.querySelectorAll(".tab-btn").forEach(tabBtn => {
        tabBtn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

            tabBtn.classList.add("active");
            const paneId = tabBtn.dataset.tab;
            const pane = document.getElementById(paneId);
            if (pane) {
                pane.classList.add("active");
                if (paneId === "tab-map") {
                    mapManager.invalidateSize();
                }
            }
        });
    });

    // 7. Modals Open / Close Handlers
    document.getElementById("btnSavedPlans").addEventListener("click", () => {
        loadSavedPlansList();
        savedModal.classList.remove("hidden");
    });

    document.getElementById("btnArchitecture").addEventListener("click", () => {
        archModal.classList.remove("hidden");
    });

    document.getElementById("btnSettings").addEventListener("click", () => {
        loadCurrentConfig();
        settingsModal.classList.remove("hidden");
    });

    document.querySelectorAll("[data-close]").forEach(el => {
        el.addEventListener("click", (e) => {
            const modalId = el.dataset.close;
            document.getElementById(modalId).classList.add("hidden");
        });
    });

    window.addEventListener("click", (e) => {
        if (e.target.classList.contains("modal-overlay")) {
            e.target.classList.add("hidden");
        }
    });

    // 8. Form Submission & Agent Execution
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const destination = document.getElementById("destinationInput").value.trim();
        const origin = document.getElementById("originInput").value.trim() || "New York";
        const duration = parseInt(durationRange.value, 10);
        const travelers = parseInt(document.getElementById("travelersCount").value, 10);
        const budget = document.querySelector('input[name="budgetTier"]:checked')?.value || "Moderate";
        const travelStyle = document.getElementById("travelStyle").value;
        const specialReqs = document.getElementById("specialReqs").value.trim();

        const interests = [];
        document.querySelectorAll(".interest-chip input:checked").forEach(cb => {
            interests.push(cb.value);
        });

        const requestPayload = {
            destination,
            origin,
            duration_days: duration,
            travelers,
            budget,
            travel_style: travelStyle,
            interests: interests.length > 0 ? interests : ["Sightseeing", "Food", "Culture"],
            special_requirements: specialReqs
        };

        // UI Loading State
        setLoadingState(true);
        thoughtConsole.classList.add("visible");
        logToggleLabel.textContent = "Hide Agent Thought Stream";

        appendLog("System", `Starting LangGraph multi-agent run for ${destination}...`);

        // Initialize Stream Client
        streamClient = new AgentStreamClient({
            onStart: (data) => {
                appendLog("Supervisor", "Multi-Agent graph entered. Analyzing travel intent...");
            },
            onLog: (data) => {
                appendLog(data.agent, data.thought || data.action);
            },
            onComplete: (finalPlan) => {
                appendLog("Aggregator", "Master travel dossier created & persisted!");
                currentPlan = finalPlan;
                renderCompletePlan(finalPlan);
                setLoadingState(false);
                updateSavedPlansBadge();
            },
            onError: async (errMsg) => {
                console.warn("[Stream] Falling back to REST API:", errMsg);
                appendLog("System", `WebSocket streaming notification: fallback to REST executor.`);
                await executeViaREST(requestPayload);
            }
        });

        try {
            streamClient.resetAgentPipelineUI();
            streamClient.connect(requestPayload);
        } catch (err) {
            console.warn("WebSocket initiation failed, using REST fallback:", err);
            await executeViaREST(requestPayload);
        }
    });

    // Fallback REST Executor
    async function executeViaREST(payload) {
        try {
            const resp = await fetch("/api/plan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const result = await resp.json();
            if (result.success && result.data) {
                currentPlan = result.data;
                if (streamClient) streamClient.markAllAgentsDone();
                renderCompletePlan(result.data);
                appendLog("Response Aggregator", "Plan successfully generated via REST fallback.");
                updateSavedPlansBadge();
            } else {
                alert("Error generating plan: " + (result.detail || result.message || "Unknown error"));
            }
        } catch (err) {
            alert("Connection error: " + err.message);
        } finally {
            setLoadingState(false);
        }
    }

    function setLoadingState(loading) {
        if (loading) {
            generateBtn.disabled = true;
            btnSpinner.classList.remove("hidden");
            btnText.textContent = "Agents Coordinating...";
        } else {
            generateBtn.disabled = false;
            btnSpinner.classList.add("hidden");
            btnText.textContent = "Launch LangGraph Multi-Agent Team";
        }
    }

    function appendLog(agent, text) {
        const time = new Date().toLocaleTimeString();
        const line = document.createElement("div");
        line.className = "log-line";
        line.innerHTML = `
            <span class="log-time">[${time}]</span>
            <span class="log-agent">[${agent}]</span>
            <span class="log-msg">${escapeHtml(text)}</span>
        `;
        thoughtLogsList.appendChild(line);
        thoughtLogsList.scrollTop = thoughtLogsList.scrollHeight;
    }

    // 9. Render Master Plan
    function renderCompletePlan(plan) {
        emptyState.classList.add("hidden");
        planContainer.classList.remove("hidden");

        // Hero Section
        document.getElementById("heroDestination").textContent = plan.destination;
        document.getElementById("heroDuration").textContent = `${plan.duration_days} Days`;
        document.getElementById("heroBudget").textContent = `${plan.budget_tier} Tier`;
        document.getElementById("heroTravelers").textContent = `${plan.travelers} Traveler${plan.travelers > 1 ? 's' : ''}`;
        document.getElementById("heroTitle").textContent = plan.title;
        document.getElementById("heroSummary").textContent = plan.executive_summary;

        // 1. Overview Tab
        renderOverviewTab(plan);

        // 2. Itinerary Tab
        renderItineraryTab(plan.itinerary || []);

        // 3. Hotels Tab
        renderHotelsTab(plan.accommodations || []);

        // 4. Transport Tab
        renderTransportTab(plan.transport || []);

        // 5. Map Tab
        mapManager.renderPlanLocations(plan);

        // 6. Budget Tab
        renderBudgetTab(plan.budget_breakdown || {});

        // 7. Packing Tab
        renderPackingTab(plan.packing_checklist || []);

        // Reset to first tab
        document.querySelector('.tab-btn[data-tab="tab-overview"]').click();

        // Smooth scroll to results
        planContainer.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function renderOverviewTab(plan) {
        const weather = plan.weather || {};
        const weatherContent = document.getElementById("weatherContent");
        weatherContent.innerHTML = `
            <div class="weather-box">
                <div class="weather-temp-main">${weather.temperature_range || "Pleasant"}</div>
                <div class="weather-condition">Condition: ${weather.condition || "Clear Skies"}</div>
                <div class="weather-meta">
                    <strong>Precipitation:</strong> ${weather.rain_probability || "Low"}<br>
                    <strong>Best Season:</strong> ${weather.best_time_to_visit || "Spring/Autumn"}<br>
                    <strong>Packing Advice:</strong> ${weather.clothing_advice || "Comfortable layers."}
                </div>
            </div>
        `;

        const insights = plan.destination_insights || {};
        document.getElementById("factCurrency").textContent = insights.currency || "USD / Local";
        document.getElementById("factLanguage").textContent = insights.language || "English / Local";
        document.getElementById("factSafety").textContent = insights.safety_rating || "Safe (9/10)";
        document.getElementById("factVisa").textContent = insights.visa_requirements || "Check local embassy";

        const tipsList = document.getElementById("culturalTipsList");
        tipsList.innerHTML = (insights.cultural_tips || [])
            .map(tip => `<li>${escapeHtml(tip)}</li>`)
            .join("");

        const attractionsCloud = document.getElementById("topAttractionsCloud");
        attractionsCloud.innerHTML = (insights.top_attractions || [])
            .map(att => `<span class="attraction-tag">📍 ${escapeHtml(att)}</span>`)
            .join("");
    }

    function renderItineraryTab(days) {
        const container = document.getElementById("itineraryTimeline");
        container.innerHTML = days.map(day => `
            <div class="day-card">
                <div class="day-header">
                    <div class="day-title-group">
                        <h3>${escapeHtml(day.title)}</h3>
                        <div class="day-summary">${escapeHtml(day.summary)}</div>
                    </div>
                    <div class="day-cost-tag">Est. $${day.daily_cost_estimate || 45}/day</div>
                </div>
                <div class="day-body">
                    ${(day.items || []).map(item => `
                        <div class="time-slot-item">
                            <div class="slot-time">${escapeHtml(item.time_slot)}</div>
                            <div class="slot-content">
                                <h5>${escapeHtml(item.activity)}</h5>
                                <p>${escapeHtml(item.description)}</p>
                            </div>
                        </div>
                    `).join("")}
                    <div class="dining-recommendations">
                        <div class="dining-box">
                            <div class="dining-label">🍽️ Recommended Lunch Spot:</div>
                            <div>${escapeHtml(day.lunch_suggestion)}</div>
                        </div>
                        <div class="dining-box">
                            <div class="dining-label">🍷 Recommended Dinner Spot:</div>
                            <div>${escapeHtml(day.dinner_suggestion)}</div>
                        </div>
                    </div>
                </div>
            </div>
        `).join("");
    }

    function renderHotelsTab(hotels) {
        const container = document.getElementById("hotelsGrid");
        container.innerHTML = hotels.map(hotel => `
            <div class="hotel-card">
                <div>
                    ${hotel.badge ? `<div class="hotel-badge">${escapeHtml(hotel.badge)}</div>` : ''}
                    <h3 class="hotel-name">${escapeHtml(hotel.name)}</h3>
                    <div class="hotel-rating">★ ${hotel.rating} • ${escapeHtml(hotel.type)}</div>
                    <p class="hotel-desc">${escapeHtml(hotel.description)}</p>
                    <div class="hotel-amenities">
                        ${(hotel.amenities || []).map(a => `<span class="amenity-pill">${escapeHtml(a)}</span>`).join("")}
                    </div>
                </div>
                <div class="hotel-footer">
                    <div>
                        <div class="text-muted text-sm">Total ${hotel.total_price ? `($${hotel.total_price})` : ''}</div>
                        <div class="hotel-price">$${hotel.price_per_night} <span>/ night</span></div>
                    </div>
                    <button class="btn btn-secondary btn-xs" onclick="alert('Booking reservation link preview: ${hotel.name}')">View Stay</button>
                </div>
            </div>
        `).join("");
    }

    function renderTransportTab(transports) {
        const container = document.getElementById("transportGrid");
        container.innerHTML = transports.map(item => `
            <div class="transport-card">
                <div>
                    <div class="trans-category">${escapeHtml(item.category)}</div>
                    <div class="trans-title">${escapeHtml(item.title)}</div>
                    <div class="trans-meta">
                        <strong>Provider:</strong> ${escapeHtml(item.provider)}<br>
                        <strong>Route:</strong> ${escapeHtml(item.route)} • <strong>Duration:</strong> ${escapeHtml(item.duration)}<br>
                        <strong>Schedule:</strong> ${escapeHtml(item.frequency_or_schedule)}
                    </div>
                    <div class="trans-tips">💡 ${escapeHtml(item.tips)}</div>
                </div>
                <div class="trans-cost">
                    <div class="text-muted text-sm">Estimated Total</div>
                    <div class="trans-price">$${item.estimated_price}</div>
                </div>
            </div>
        `).join("");
    }

    function renderBudgetTab(budget) {
        const total = budget.total_estimated || 0;
        const perPerson = budget.cost_per_person || 0;
        document.getElementById("totalCostDisplay").textContent = `$${total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        document.getElementById("perPersonDisplay").textContent = `($${perPerson.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} per person)`;

        const categories = [
            { label: "Flight & Transit", val: budget.transport || 0, color: "var(--accent-primary)" },
            { label: "Lodging & Accommodations", val: budget.accommodation || 0, color: "var(--accent-purple)" },
            { label: "Sightseeing & Experiences", val: budget.activities_and_attractions || 0, color: "var(--accent-secondary)" },
            { label: "Dining & Culinary", val: budget.food_and_dining || 0, color: "var(--accent-amber)" },
            { label: "Contingency & Buffer", val: budget.miscellaneous_and_buffer || 0, color: "var(--accent-emerald)" }
        ];

        const container = document.getElementById("expenseBarsContainer");
        container.innerHTML = categories.map(cat => {
            const pct = total > 0 ? Math.round((cat.val / total) * 100) : 0;
            return `
                <div class="expense-item">
                    <div class="expense-label-row">
                        <span>${cat.label}</span>
                        <span>$${cat.val.toLocaleString()} (${pct}%)</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width: ${pct}%; background: ${cat.color};"></div>
                    </div>
                </div>
            `;
        }).join("");
    }

    function renderPackingTab(items) {
        const container = document.getElementById("packingChecklist");
        container.innerHTML = items.map((item, idx) => `
            <div class="checklist-item" onclick="this.classList.toggle('checked')">
                <input type="checkbox" id="pack_${idx}">
                <label for="pack_${idx}" style="cursor:pointer;">${escapeHtml(item)}</label>
            </div>
        `).join("");
    }

    // 10. Saved Plans Management
    async function loadSavedPlansList() {
        const listEl = document.getElementById("savedPlansList");
        listEl.innerHTML = `<div class="loading-state">Loading your trips...</div>`;
        try {
            const resp = await fetch("/api/plans");
            const plans = await resp.json();
            if (!plans || plans.length === 0) {
                listEl.innerHTML = `<p class="text-muted">No saved trips yet. Generate your first trip plan!</p>`;
                return;
            }

            listEl.innerHTML = plans.map(p => `
                <div class="saved-plan-row" style="display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid var(--border-glass);">
                    <div>
                        <strong style="font-size:0.95rem; color:#fff;">${escapeHtml(p.title)}</strong><br>
                        <span class="text-sm text-muted">${p.duration_days} Days • ${escapeHtml(p.budget_category)} • Created: ${new Date(p.created_at).toLocaleDateString()}</span>
                    </div>
                    <div style="display:flex; gap:8px;">
                        <button class="btn btn-primary btn-xs" onclick="window.loadPlanById('${p.id}')">View</button>
                        <button class="btn btn-outline btn-xs" onclick="window.deletePlanById('${p.id}')">Delete</button>
                    </div>
                </div>
            `).join("");
        } catch (e) {
            listEl.innerHTML = `<p style="color:#ef4444;">Error loading plans: ${e.message}</p>`;
        }
    }

    window.loadPlanById = async (planId) => {
        try {
            const resp = await fetch(`/api/plans/${planId}`);
            const data = await resp.json();
            if (data && data.plan_data) {
                savedModal.classList.add("hidden");
                currentPlan = data.plan_data;
                renderCompletePlan(data.plan_data);
            }
        } catch (e) {
            alert("Error fetching plan: " + e.message);
        }
    };

    window.deletePlanById = async (planId) => {
        if (!confirm("Are you sure you want to delete this trip plan?")) return;
        try {
            await fetch(`/api/plans/${planId}`, { method: "DELETE" });
            loadSavedPlansList();
            updateSavedPlansBadge();
        } catch (e) {
            alert("Error deleting plan: " + e.message);
        }
    };

    async function updateSavedPlansBadge() {
        try {
            const resp = await fetch("/api/plans");
            const plans = await resp.json();
            if (Array.isArray(plans)) {
                savedCountBadge.textContent = plans.length;
            }
        } catch (e) {}
    }

    // 11. Settings & Config
    async function loadCurrentConfig() {
        try {
            const resp = await fetch("/api/config");
            const cfg = await resp.json();
            document.getElementById("cfgLangsmith").checked = cfg.langsmith_tracing;
            const langsmithGroup = document.getElementById("langsmithKeyGroup");
            langsmithGroup.classList.toggle("hidden", !cfg.langsmith_tracing);
        } catch (e) {}
    }

    document.getElementById("cfgLangsmith").addEventListener("change", (e) => {
        document.getElementById("langsmithKeyGroup").classList.toggle("hidden", !e.target.checked);
    });

    document.getElementById("settingsForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = {
            openai_api_key: document.getElementById("cfgOpenAiKey").value || null,
            gemini_api_key: document.getElementById("cfgGeminiKey").value || null,
            groq_api_key: document.getElementById("cfgGroqKey").value || null,
            openweather_api_key: document.getElementById("cfgWeatherKey").value || null,
            langchain_tracing_v2: document.getElementById("cfgLangsmith").checked,
            langchain_api_key: document.getElementById("cfgLangsmithKey")?.value || null
        };

        try {
            await fetch("/api/config", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            alert("Settings updated successfully!");
            settingsModal.classList.add("hidden");
        } catch (err) {
            alert("Error saving settings: " + err.message);
        }
    });

    // 12. Export Tools
    document.getElementById("btnPrintPlan").addEventListener("click", () => {
        window.print();
    });

    document.getElementById("btnCopyMarkdown").addEventListener("click", () => {
        if (!currentPlan) return;
        let md = `# ${currentPlan.title}\n\n`;
        md += `**Destination:** ${currentPlan.destination} | **Duration:** ${currentPlan.duration_days} Days | **Budget:** ${currentPlan.budget_tier}\n\n`;
        md += `## Executive Summary\n${currentPlan.executive_summary}\n\n`;
        md += `## Day-by-Day Itinerary\n`;
        (currentPlan.itinerary || []).forEach(day => {
            md += `### ${day.title}\n*${day.summary}*\n`;
            (day.items || []).forEach(item => {
                md += `- **${item.time_slot}**: ${item.activity} - ${item.description}\n`;
            });
            md += `- **Lunch:** ${day.lunch_suggestion}\n- **Dinner:** ${day.dinner_suggestion}\n\n`;
        });
        md += `## Estimated Budget\nTotal: $${currentPlan.budget_breakdown?.total_estimated} ($${currentPlan.budget_breakdown?.cost_per_person} per person)\n`;

        navigator.clipboard.writeText(md).then(() => {
            alert("Plan Markdown copied to clipboard!");
        });
    });

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initial check
    updateSavedPlansBadge();
});
