/**
 * Company Events Page JavaScript
 * Handles interactive elements and visualizations on the events page
 */

// Chart configuration and utilities
const chartColors = {
  primary: '#27ae60',
  secondary: '#3498db',
  warning: '#f39c12',
  danger: '#e74c3c',
  light: '#ecf0f1',
  dark: '#2c3e50',
  travelColor: '#3498db',
  venueColor: '#e74c3c',
  accommodationColor: '#f39c12',
  cateringColor: '#2ecc71',
  materialsColor: '#9b59b6',
  digitalColor: '#1abc9c'
};

// Store charts as global variables for easy access
let emissionsChart = null;
let trendChart = null;
let eventEmissionsChart = null;

/**
 * Initialize charts when the DOM is fully loaded
 */
document.addEventListener('DOMContentLoaded', function() {
  // Initialize main charts
  initEmissionsChart();
  initTrendChart();
  
  // Initialize interactive elements
  initEmissionCategories();
  initEventTypeToggle();
  initQuarterlyToggle();
  
  // Add animation to equivalence cards
  initEquivalenceCards();
  
  // Initialize carbon badge tooltips
  initTooltips();
});

/**
 * Initialize the emissions breakdown doughnut chart
 */
function initEmissionsChart() {
  const emissionsCtx = document.getElementById('emissionsChart');
  if (!emissionsCtx) return;
  
  // Get data from the data attributes
  const labels = JSON.parse(emissionsCtx.dataset.labels || '[]');
  const data = JSON.parse(emissionsCtx.dataset.values || '[]');
  
  emissionsChart = new Chart(emissionsCtx.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: [
          chartColors.travelColor,
          chartColors.venueColor,
          chartColors.accommodationColor,
          chartColors.cateringColor,
          chartColors.materialsColor,
          chartColors.digitalColor
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const value = context.raw;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return `${value} kg CO₂e (${percentage}%)`;
            }
          }
        }
      },
      cutout: '65%',
      animation: {
        animateScale: true,
        animateRotate: true
      }
    }
  });
}

/**
 * Initialize the quarterly trend bar chart
 */
function initTrendChart() {
  const trendCtx = document.getElementById('trendChart');
  if (!trendCtx) return;
  
  // Get data from the data attributes
  const labels = JSON.parse(trendCtx.dataset.labels || '[]');
  const data = JSON.parse(trendCtx.dataset.values || '[]');
  
  trendChart = new Chart(trendCtx.getContext('2d'), {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Total Emissions (kg CO₂e)',
        data: data,
        backgroundColor: chartColors.primary,
        borderColor: chartColors.primary,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'kg CO₂e'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Quarter'
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  });
}

/**
 * Make emission category cards interactive
 */
function initEmissionCategories() {
  const emissionCategories = document.querySelectorAll('.emission-category');
  if (!emissionCategories.length) return;
  
  emissionCategories.forEach(category => {
    category.addEventListener('click', function() {
      const index = parseInt(this.dataset.index);
      
      // Toggle active state
      if (this.classList.contains('active')) {
        // If already active, deactivate and reset all
        emissionCategories.forEach(cat => {
          cat.classList.remove('active', 'dimmed');
        });
        
        // Reset chart highlights
        if (emissionsChart) {
          emissionsChart.setActiveElements([]);
          emissionsChart.update();
        }
      } else {
        // Set this as active, dim others
        emissionCategories.forEach(cat => {
          if (cat === this) {
            cat.classList.add('active');
            cat.classList.remove('dimmed');
          } else {
            cat.classList.remove('active');
            cat.classList.add('dimmed');
          }
        });
        
        // Highlight corresponding chart segment
        if (emissionsChart) {
          emissionsChart.setActiveElements([{
            datasetIndex: 0,
            index: index
          }]);
          emissionsChart.update();
        }
      }
    });
    
    // Add hover effects
    category.addEventListener('mouseenter', function() {
      if (!this.classList.contains('active') && !document.querySelector('.emission-category.active')) {
        // Only highlight on hover if no categories are active
        const index = parseInt(this.dataset.index);
        if (emissionsChart) {
          emissionsChart.setActiveElements([{
            datasetIndex: 0,
            index: index
          }]);
          emissionsChart.update();
        }
      }
    });
    
    category.addEventListener('mouseleave', function() {
      if (!this.classList.contains('active') && !document.querySelector('.emission-category.active')) {
        // Reset highlights when mouse leaves if not active
        if (emissionsChart) {
          emissionsChart.setActiveElements([]);
          emissionsChart.update();
        }
      }
    });
  });
}

/**
 * Initialize the event type toggle (Virtual/In-Person)
 */
function initEventTypeToggle() {
  const eventTypeToggle = document.getElementById('eventTypeToggle');
  if (!eventTypeToggle) return;
  
  const eventTypeOptions = eventTypeToggle.querySelectorAll('.event-type-option');
  
  eventTypeOptions.forEach(option => {
    option.addEventListener('click', function() {
      const type = this.dataset.type;
      eventTypeToggle.className = 'event-type-toggle ' + type;
      
      // Get data based on the selected event type
      fetch(`/company/api/events_by_type?type=${type}`)
        .then(response => response.json())
        .then(data => {
          // Update emissions chart with the filtered data
          if (emissionsChart) {
            emissionsChart.data.datasets[0].data = data.emissions;
            emissionsChart.update();
          }
        })
        .catch(error => {
          console.error('Error fetching event type data:', error);
          
          // Fallback data for demonstration
          if (emissionsChart) {
            if (type === 'virtual') {
              // Show more digital, less travel for virtual events
              emissionsChart.data.datasets[0].data = [5, 0, 0, 0, 10, 85];
            } else {
              // Show balanced data for in-person
              emissionsChart.data.datasets[0].data = [40, 20, 15, 15, 10, 0];
            }
            emissionsChart.update();
          }
        });
    });
  });
}

/**
 * Initialize quarterly/monthly toggle for trend chart
 */
function initQuarterlyToggle() {
  const toggleQuarterlyView = document.getElementById('toggleQuarterlyView');
  if (!toggleQuarterlyView) return;
  
  let isQuarterlyView = true;
  
  toggleQuarterlyView.addEventListener('click', function() {
    isQuarterlyView = !isQuarterlyView;
    const toggleText = this.querySelector('.toggle-text');
    
    if (isQuarterlyView) {
      toggleText.textContent = 'Quarterly View';
      fetchTrendData('quarterly');
    } else {
      toggleText.textContent = 'Monthly View';
      fetchTrendData('monthly');
    }
  });
  
  function fetchTrendData(interval) {
    fetch(`/company/api/trend_data?interval=${interval}`)
      .then(response => response.json())
      .then(data => {
        if (trendChart) {
          trendChart.data.labels = data.labels;
          trendChart.data.datasets[0].data = data.emissions;
          trendChart.options.scales.x.title.text = interval === 'quarterly' ? 'Quarter' : 'Month';
          trendChart.update();
        }
      })
      .catch(error => {
        console.error(`Error fetching ${interval} trend data:`, error);
        
        // Fallback data for demonstration
        if (trendChart) {
          if (interval === 'quarterly') {
            trendChart.data.labels = ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025'];
            trendChart.data.datasets[0].data = [1200, 980, 850, 1050];
          } else {
            trendChart.data.labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            trendChart.data.datasets[0].data = [400, 380, 420, 350, 320, 310, 290, 280, 280, 340, 360, 350];
          }
          trendChart.options.scales.x.title.text = interval === 'quarterly' ? 'Quarter' : 'Month';
          trendChart.update();
        }
      });
  }
}

/**
 * Initialize event details modal and chart
 */
function showEventDetails(eventId) {
  const modal = document.getElementById('eventDetailsModal');
  if (!modal) return;
  
  const loading = modal.querySelector('.event-loading');
  const details = modal.querySelector('.event-details');
  
  // Show loading, hide details
  loading.style.display = 'block';
  details.style.display = 'none';
  
  // Show the modal
  $('#eventDetailsModal').modal('show');
  
  // Fetch event details
  fetch(`/company/api/event/${eventId}`)
    .then(response => response.json())
    .then(event => {
      // Update modal content with event data
      document.getElementById('eventDetailsModalLabel').textContent = event.name;
      document.getElementById('eventDate').textContent = `${event.start_date} to ${event.end_date}`;
      document.getElementById('eventLocation').textContent = event.is_virtual ? 'Virtual Event' : event.location;
      document.getElementById('eventAttendees').textContent = `${event.attendees_count} attendees`;
      document.getElementById('eventType').textContent = event.event_type;
      document.getElementById('eventDescription').textContent = event.description;
      
      // Set sustainability score
      const scoreElement = document.getElementById('sustainabilityScore');
      const scoreValue = document.getElementById('scoreValue');
      scoreValue.textContent = event.sustainability_score;
      
      // Set score color based on value
      let scoreColor, scoreText;
      if (event.sustainability_score >= 80) {
        scoreColor = chartColors.primary;
        scoreText = 'Excellent sustainability practices';
      } else if (event.sustainability_score >= 60) {
        scoreColor = chartColors.secondary;
        scoreText = 'Good sustainability practices';
      } else if (event.sustainability_score >= 40) {
        scoreColor = chartColors.warning;
        scoreText = 'Average sustainability practices';
      } else {
        scoreColor = chartColors.danger;
        scoreText = 'Needs improvement';
      }
      
      scoreElement.style.backgroundColor = scoreColor;
      document.getElementById('scoreText').textContent = scoreText;
      
      // Set offset percentage
      document.getElementById('offsetPercentage').textContent = `${event.carbon_offset_percentage}%`;
      document.getElementById('offsetProgress').style.width = `${event.carbon_offset_percentage}%`;
      document.getElementById('offsetText').textContent = `${event.co2_offset} kg CO₂e offset through sustainability initiatives`;
      
      // Set initiatives list
      const initiativesList = document.getElementById('initiativesList');
      initiativesList.innerHTML = '';
      
      if (event.sustainability_initiatives && event.sustainability_initiatives.length > 0) {
        event.sustainability_initiatives.forEach(initiative => {
          const li = document.createElement('li');
          li.textContent = initiative;
          initiativesList.appendChild(li);
        });
      } else {
        const li = document.createElement('li');
        li.textContent = 'No sustainability initiatives recorded for this event.';
        initiativesList.appendChild(li);
      }
      
      // Set impact equivalents
      document.getElementById('treesValue').textContent = event.impact_equivalents.trees_planted;
      document.getElementById('carMilesValue').textContent = event.impact_equivalents.car_miles.toLocaleString();
      
      // Create emissions breakdown chart
      const chartCtx = document.getElementById('eventEmissionsChart').getContext('2d');
      
      // Destroy existing chart if it exists
      if (eventEmissionsChart) {
        eventEmissionsChart.destroy();
      }
      
      eventEmissionsChart = new Chart(chartCtx, {
        type: 'bar',
        data: {
          labels: event.emissions_breakdown.labels,
          datasets: [{
            label: 'kg CO₂e',
            data: event.emissions_breakdown.data,
            backgroundColor: [
              chartColors.travelColor,
              chartColors.venueColor,
              chartColors.accommodationColor,
              chartColors.cateringColor,
              chartColors.materialsColor,
              chartColors.digitalColor
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'kg CO₂e'
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `${context.raw} kg CO₂e (${(context.raw / event.total_emissions * 100).toFixed(1)}%)`;
                }
              }
            }
          },
          animation: {
            duration: 1000,
            easing: 'easeOutQuart'
          }
        }
      });
      
      // Hide loading, show details
      loading.style.display = 'none';
      details.style.display = 'block';
    })
    .catch(error => {
      console.error('Error fetching event details:', error);
      loading.innerHTML = `<div class="alert alert-danger">Error loading event details. Please try again.</div>`;
    });
}

/**
 * Initialize equivalence cards with animation effects
 */
function initEquivalenceCards() {
  const cards = document.querySelectorAll('.equivalence-card');
  if (!cards.length) return;
  
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateX(8px)';
      this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateX(0)';
      this.style.boxShadow = 'none';
    });
  });
}

/**
 * Initialize tooltips for carbon badges
 */
function initTooltips() {
  const badges = document.querySelectorAll('.carbon-badge');
  if (!badges.length) return;
  
  badges.forEach(badge => {
    // Add tooltip data
    badge.title = 'Carbon footprint impact';
    badge.dataset.toggle = 'tooltip';
    badge.dataset.placement = 'top';
    
    // Initialize tooltip
    $(badge).tooltip();
  });
}