/**
 * Leaflet Interactive Map Module
 */

class TravelMapManager {
    constructor(elementId) {
        this.elementId = elementId;
        this.map = null;
        this.markers = [];
    }

    init(lat = 35.6762, lon = 139.6503, zoom = 12) {
        const container = document.getElementById(this.elementId);
        if (!container) return;

        if (this.map) {
            this.map.remove();
            this.map = null;
        }

        // Initialize Leaflet map
        this.map = L.map(this.elementId).setView([lat, lon], zoom);

        // Add CartoDB Dark Matter tiles (looks gorgeous with dark UI theme!)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(this.map);
    }

    renderPlanLocations(plan) {
        if (!this.map) {
            const destLat = plan?.destination_insights?.coordinates?.lat || 48.8566;
            const destLon = plan?.destination_insights?.coordinates?.lon || 2.3522;
            this.init(destLat, destLon, 12);
        }

        // Clear existing markers
        this.markers.forEach(m => this.map.removeLayer(m));
        this.markers = [];

        const bounds = [];

        // 1. Add Hotel Markers
        const hotels = plan.accommodations || [];
        hotels.forEach((h, idx) => {
            if (h.lat && h.lon) {
                const marker = L.marker([h.lat, h.lon], {
                    title: h.name
                }).addTo(this.map);

                marker.bindPopup(`
                    <div style="color:#0f172a; font-family:sans-serif; min-width:160px;">
                        <strong style="color:#4f46e5;">🏨 ${h.name}</strong><br>
                        <span style="font-size:12px; color:#475569;">${h.type} • ★ ${h.rating}</span><br>
                        <strong style="color:#059669;">$${h.price_per_night}/night</strong>
                    </div>
                `);
                this.markers.push(marker);
                bounds.push([h.lat, h.lon]);
            }
        });

        // 2. Add Itinerary Attractions Markers
        const days = plan.itinerary || [];
        days.forEach(day => {
            (day.items || []).forEach(item => {
                if (item.lat && item.lon) {
                    const marker = L.circleMarker([item.lat, item.lon], {
                        radius: 8,
                        fillColor: "#6366f1",
                        color: "#fff",
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.9
                    }).addTo(this.map);

                    marker.bindPopup(`
                        <div style="color:#0f172a; font-family:sans-serif; max-width:200px;">
                            <strong style="color:#6366f1;">📍 Day ${day.day}: ${item.activity}</strong><br>
                            <span style="font-size:11px; color:#475569;">${item.location}</span><br>
                            <p style="font-size:12px; margin:4px 0 0;">${item.description}</p>
                        </div>
                    `);
                    this.markers.push(marker);
                    bounds.push([item.lat, item.lon]);
                }
            });
        });

        // Adjust bounds to show all markers
        if (bounds.length > 0) {
            try {
                this.map.fitBounds(bounds, { padding: [40, 40] });
            } catch (e) {
                console.warn("Could not fit map bounds:", e);
            }
        }
    }

    invalidateSize() {
        if (this.map) {
            setTimeout(() => {
                this.map.invalidateSize();
            }, 200);
        }
    }
}

window.TravelMapManager = TravelMapManager;
