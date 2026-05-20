// Wait for full page load before drawing charts
window.addEventListener('load', function () {

    // Attack Types — Pie Chart
    fetch('/api/types')
        .then(res => res.json())
        .then(data => {
            if (!Object.keys(data).length) return;
            new Chart(document.getElementById('typeChart'), {
                type: 'pie',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        data: Object.values(data),
                        backgroundColor: ['#ef4444', '#3b82f6', '#f59e0b', '#22c55e', '#a855f7'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#ccc', font: { size: 12 } } } }
                }
            });
        })
        .catch(err => console.error('types error:', err));

    // Top IPs — Bar Chart
    fetch('/api/ips')
        .then(res => res.json())
        .then(data => {
            if (!Object.keys(data).length) return;
            new Chart(document.getElementById('ipChart'), {
                type: 'bar',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        label: 'Attacks',
                        data: Object.values(data),
                        backgroundColor: '#3b82f6',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { color: '#888', stepSize: 1 }, grid: { color: '#1e1e2e' } },
                        x: { ticks: { color: '#888' }, grid: { display: false } }
                    }
                }
            });
        })
        .catch(err => console.error('ips error:', err));

    // Attack Trend — Line Chart
    fetch('/api/trend')
        .then(res => res.json())
        .then(data => {
            if (!Object.keys(data).length) return;
            new Chart(document.getElementById('trendChart'), {
                type: 'line',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        label: 'Attacks per day',
                        data: Object.values(data),
                        fill: true,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239,68,68,0.15)',
                        tension: 0.4,
                        pointBackgroundColor: '#ef4444',
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#ccc' } } },
                    scales: {
                        y: { beginAtZero: true, ticks: { color: '#888', stepSize: 1 }, grid: { color: '#1e1e2e' } },
                        x: { ticks: { color: '#888' }, grid: { display: false } }
                    }
                }
            });
        })
        .catch(err => console.error('trend error:', err));

});
