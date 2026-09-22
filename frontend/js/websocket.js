/**
 * WebSocket Streaming Client for LangGraph Multi-Agent Travel Planner
 */

class AgentStreamClient {
    constructor(callbacks) {
        this.callbacks = callbacks || {};
        this.socket = null;
        this.sessionId = null;
    }

    connect(payload) {
        this.sessionId = 'session_' + Math.random().toString(36).substring(2, 10);
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
            console.log("[WebSocket] Connected to agent stream:", wsUrl);
            if (this.callbacks.onConnected) this.callbacks.onConnected();
            // Transmit user travel planning payload
            this.socket.send(JSON.stringify(payload));
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleEvent(data);
            } catch (err) {
                console.error("[WebSocket] Parse error:", err, event.data);
            }
        };

        this.socket.onerror = (error) => {
            console.warn("[WebSocket] Error (falling back to REST):", error);
            if (this.callbacks.onError) this.callbacks.onError(error);
        };

        this.socket.onclose = () => {
            console.log("[WebSocket] Closed stream.");
            if (this.callbacks.onClosed) this.callbacks.onClosed();
        };
    }

    handleEvent(data) {
        const type = data.type;

        if (type === 'agent_start') {
            if (this.callbacks.onStart) this.callbacks.onStart(data);
        } else if (type === 'agent_log') {
            if (this.callbacks.onLog) this.callbacks.onLog(data);
            this.updateAgentPipelineUI(data.agent, data.thought);
        } else if (type === 'workflow_complete') {
            this.markAllAgentsDone();
            if (this.callbacks.onComplete) this.callbacks.onComplete(data.final_plan);
        } else if (type === 'error') {
            if (this.callbacks.onError) this.callbacks.onError(data.message);
        }
    }

    updateAgentPipelineUI(agentName, thought) {
        const nameLower = (agentName || "").toLowerCase();
        let targetId = null;

        if (nameLower.includes("supervisor")) targetId = "agent-supervisor";
        else if (nameLower.includes("destination")) targetId = "agent-destination";
        else if (nameLower.includes("itinerary")) targetId = "agent-itinerary";
        else if (nameLower.includes("accommodation")) targetId = "agent-accommodation";
        else if (nameLower.includes("transport")) targetId = "agent-transport";
        else if (nameLower.includes("aggregator")) targetId = "agent-aggregator";

        if (targetId) {
            const card = document.getElementById(targetId);
            if (card) {
                // Clear active from others
                document.querySelectorAll(".agent-card").forEach(c => c.classList.remove("agent-active"));
                card.classList.add("agent-active");
                card.classList.add("agent-completed");
                const badge = card.querySelector(".agent-status-badge");
                if (badge) {
                    badge.textContent = "Processing...";
                    badge.className = "agent-status-badge status-running";
                }
            }
        }
    }

    markAllAgentsDone() {
        document.querySelectorAll(".agent-card").forEach(card => {
            card.classList.remove("agent-active");
            card.classList.add("agent-completed");
            const badge = card.querySelector(".agent-status-badge");
            if (badge) {
                badge.textContent = "Done ✓";
                badge.className = "agent-status-badge status-done";
            }
        });
    }

    resetAgentPipelineUI() {
        document.querySelectorAll(".agent-card").forEach(card => {
            card.classList.remove("agent-active", "agent-completed");
            const badge = card.querySelector(".agent-status-badge");
            if (badge) {
                badge.textContent = "Idle";
                badge.className = "agent-status-badge status-idle";
            }
        });
    }
}

window.AgentStreamClient = AgentStreamClient;
