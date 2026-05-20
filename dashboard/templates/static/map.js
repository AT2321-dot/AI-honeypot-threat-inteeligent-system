var map = L.map('map').setView([20, 0], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

fetch('/api/map')
    .then(res => res.json())
    .then(data => {
        data.forEach(item => {
            L.marker([item.lat, item.lon])
                .addTo(map)
                // Fix: API now returns item.country; also show attack_type
                .bindPopup(`<b>IP:</b> ${item.ip}<br><b>Country:</b> ${item.country}<br><b>Type:</b> ${item.attack_type}`);
        });
    })
    .catch(err => console.error('Failed to load map data:', err));
