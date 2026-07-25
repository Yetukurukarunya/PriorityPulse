let categoryChart = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    
    // Only load these on pages that have them (officer/admin dashboards)
    const priorityQueue = document.getElementById('priorityQueue');
    if (priorityQueue) {
        loadPriorityQueue();
    }
    
    const analyticsEl = document.getElementById('totalComplaints');
    if (analyticsEl) {
        loadAnalytics();
    }
    
    const clustersEl = document.getElementById('clusterAnalysis');
    if (clustersEl) {
        loadClusters();
    }
    
    // Set up auto-refresh (every 10 seconds)
    setInterval(() => {
        if (priorityQueue) loadPriorityQueue();
        if (analyticsEl) loadAnalytics();
        if (clustersEl) loadClusters();
        
        // Refresh map if visible
        const mapView = document.getElementById('tab-map-view');
        if (mapView && mapView.classList.contains('active')) {
            if (typeof refreshMapData === 'function') {
                refreshMapData();
            }
        }
    }, 10000);
    
    // Form submission
    const complaintForm = document.getElementById('complaintForm');
    if (complaintForm) {
        complaintForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitComplaint();
        });
    }
});

function submitComplaint() {
    const complaintText = document.getElementById('complaintText').value;
    const location = document.getElementById('location').value;
    
    if (!complaintText.trim()) {
        alert('Please enter a complaint description');
        return;
    }
    
    // Show loading
    const submitBtn = document.querySelector('#complaintForm button');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    submitBtn.disabled = true;
    
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            complaint_text: complaintText,
            location: location
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showPredictionResult(data.prediction);
            document.getElementById('complaintText').value = '';
            document.getElementById('location').value = '';
            loadPriorityQueue();
            loadAnalytics();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to analyze complaint');
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

// Refresh activity table (for citizen dashboard overview)
function refreshActivity() {
    console.log('Refreshing activity data...');
    
    fetch('/get-complaints')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.complaints) {
                location.reload(); // Simple reload to refresh the page with new data
            }
        })
        .catch(error => {
            console.error('Error refreshing activity:', error);
        });
}

function showPredictionResult(prediction) {
    const resultDiv = document.getElementById('predictionResult');
    const resultContent = document.getElementById('resultContent');
    const resultHeader = document.getElementById('resultHeader');
    
    // Check if elements exist (they might not on some pages)
    if (!resultDiv || !resultContent || !resultHeader) {
        console.log('Prediction result elements not found - this is normal on some pages');
        return;
    }
    
    // Set header color based on category
    resultHeader.className = `card-header text-white bg-${prediction.color}`;
    
    resultContent.innerHTML = `
        <div class="text-center">
            <div class="severity-badge severity-${prediction.category.toLowerCase().replace(' ', '-')}">
                ${prediction.category}
            </div>
            <h2 class="mt-3">Severity Score: ${prediction.severity_score}/10</h2>
            <div class="progress mt-3">
                <div class="progress-bar bg-${prediction.color}" 
                     style="width: ${prediction.severity_score * 10}%">
                </div>
            </div>
            <p class="mt-3">
                <strong>Priority Level:</strong> ${prediction.priority_level}<br>
                <strong>Recommended Action:</strong> ${getRecommendedAction(prediction.category)}
            </p>
        </div>
    `;
    
    resultDiv.style.display = 'block';
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        resultDiv.style.display = 'none';
    }, 10000);
}

function getRecommendedAction(category) {
    switch(category) {
        case 'Emergency':
            return 'Immediate dispatch of emergency services required';
        case 'High Priority':
            return 'Assign to senior officer within 1 hour';
        case 'Medium Priority':
            return 'Schedule for resolution within 24 hours';
        case 'Low Priority':
            return 'Plan for resolution within 3-5 days';
        default:
            return 'Standard procedure follow-up';
    }
}

function loadPriorityQueue() {
    const queueContainer = document.getElementById('priorityQueue');
    if (!queueContainer) return; // Element doesn't exist on this page
    
    fetch('/get_priority_queue')
        .then(response => response.json())
        .then(data => {            
            if (data.complaints.length === 0) {
                queueContainer.innerHTML = '<p class="text-muted">No complaints submitted yet</p>';
                return;
            }
            
            let html = '';
            data.complaints.forEach(complaint => {
                const priorityClass = `priority-${complaint.category.toLowerCase().replace(' ', '-')}`;
                html += `
                    <div class="complaint-item ${priorityClass}">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <span class="badge bg-secondary">#${complaint.queue_position}</span>
                                <strong>${complaint.category}</strong>
                                <small class="text-muted ms-2">${complaint.timestamp}</small>
                                <p class="mt-2 mb-1">${complaint.text.substring(0, 100)}${complaint.text.length > 100 ? '...' : ''}</p>
                                <small><i class="fas fa-map-marker-alt"></i> ${complaint.location || 'Unknown'}</small>
                            </div>
                            <div class="text-end">
                                <span class="severity-badge severity-${complaint.category.toLowerCase().replace(' ', '-')}">
                                    Score: ${complaint.severity_score}
                                </span>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            queueContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading queue:', error);
        });
}

function loadAnalytics() {
    const totalEl = document.getElementById('totalComplaints');
    const avgEl = document.getElementById('avgSeverity');
    const chartCanvas = document.getElementById('categoryChart');
    
    // If elements don't exist, this page doesn't need analytics
    if (!totalEl || !avgEl || !chartCanvas) return;
    
    fetch('/get_analytics_data')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                totalEl.textContent = data.stats.total;
                avgEl.textContent = data.stats.avg_severity;
                updateCategoryChart(data.stats.by_category);
            }
        })
        .catch(error => {
            console.error('Error loading analytics:', error);
        });
}

function updateCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    const labels = Object.keys(categories);
    const values = Object.values(categories);
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function loadClusters() {
    const clusterContainer = document.getElementById('clusterAnalysis');
    if (!clusterContainer) return; // Element doesn't exist on this page
    
    fetch('/get_clusters')
        .then(response => response.json())
        .then(data => {            
            if (!data.clusters || data.clusters.length === 0) {
                clusterContainer.innerHTML = '<p class="text-muted">No cluster data available</p>';
                return;
            }
            
            let html = '<div class="list-group">';
            data.clusters.forEach(cluster => {
                const severityClass = cluster.avg_severity >= 8 ? 'emergency' :
                                     cluster.avg_severity >= 5 ? 'high' :
                                     cluster.avg_severity >= 3 ? 'medium' : 'low';
                
                html += `
                    <div class="cluster-card cluster-${severityClass}">
                        <strong><i class="fas fa-location-dot"></i> ${cluster.location}</strong><br>
                        <small>Avg Severity: ${cluster.avg_severity.toFixed(1)}/10</small><br>
                        <small>Complaints: ${cluster.complaint_count}</small><br>
                        <small>Common: ${cluster.common_category}</small>
                    </div>
                `;
            });
            html += '</div>';
            
            clusterContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading clusters:', error);
        });
}

function loadHeatmap() {
    const container = document.getElementById('heatmapContainer');
    container.innerHTML = '<div class="loader"></div>';
    
    fetch('/get_heatmap')
        .then(response => response.json())
        .then(data => {
            if (data.heatmap_data && data.heatmap_data.length > 0) {
                let html = '<div class="heatmap-data">';
                data.heatmap_data.slice(0, 10).forEach(point => {
                    html += `
                        <div class="complaint-item priority-${point.severity >= 8 ? 'emergency' : 
                                 point.severity >= 5 ? 'high' : 
                                 point.severity >= 3 ? 'medium' : 'low'}">
                            <small>📍 Lat: ${point.lat.toFixed(4)}, Lon: ${point.lon.toFixed(4)}</small>
                            <p class="mb-0 mt-1">${point.complaint}</p>
                            <small class="text-muted">Severity: ${point.severity}</small>
                        </div>
                    `;
                });
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p class="text-muted">No heatmap data available</p>';
            }
        })
        .catch(error => {
            console.error('Error loading heatmap:', error);
            container.innerHTML = '<p class="text-danger">Failed to load heatmap data</p>';
        });
}

function resetSession() {
    if (confirm('Are you sure you want to reset all complaints? This action cannot be undone.')) {
        fetch('/reset_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error resetting session:', error);
            alert('Failed to reset session');
        });
    }
}
// Global functions
function updateComplaintCount() {
    fetch('/get_priority_queue')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('complaint-count');
            if (badge) badge.textContent = data.total_count;
            const notificationBadge = document.getElementById('notificationBadge');
            if (notificationBadge) notificationBadge.textContent = data.total_count;
        });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function getSeverityColor(score) {
    if (score >= 8) return 'danger';
    if (score >= 5) return 'warning';
    if (score >= 3) return 'info';
    return 'success';
}

// Auto-refresh data every 30 seconds
setInterval(() => {
    updateComplaintCount();
    if (window.location.pathname === '/complaints') {
        location.reload();
    }
}, 30000);