/**
 * Dashboard functionality for Carbon Footprint Tracker
 * 
 * Handles interactive elements and dynamic content on dashboard pages
 */

/**
 * Initialize the employee dashboard
 * 
 * @param {Object} data - Dashboard data including charts data
 */
function initEmployeeDashboard(data) {
  // Initialize charts if data is available
  if (data.dates && data.scores && data.emissions) {
    if (document.getElementById('footprint-history-chart')) {
      createFootprintHistoryChart(
        'footprint-history-chart',
        JSON.parse(data.dates),
        JSON.parse(data.scores),
        JSON.parse(data.emissions)
      );
    }
  }
  
  // Setup footprint breakdown chart if available
  const breakdownElement = document.getElementById('footprint-breakdown-chart');
  if (breakdownElement && data.latestFootprint) {
    try {
      // Handle both new and legacy data models
      let footprintData = {};
      
      // For new model data (commute, office, travel breakdown)
      if ('commute_footprint' in data.latestFootprint) {
        footprintData = {
          'Commuting': data.latestFootprint.commute_footprint,
          'Office': data.latestFootprint.office_footprint,
          'Travel': data.latestFootprint.travel_footprint
        };
        
        // Add transactions if available
        if ('transaction_footprint' in data.latestFootprint && 
            'has_transaction_data' in data.latestFootprint && 
            data.latestFootprint.has_transaction_data) {
          footprintData['Transactions'] = data.latestFootprint.transaction_footprint;
        }
      } 
      // For legacy data model (calculate from lifestyle factors)
      else {
        footprintData = {
          'Commuting': calculateCommuteEmissions(data.latestFootprint),
          'Diet': calculateDietEmissions(data.latestFootprint),
          'Office': calculateOfficeEmissions(data.latestFootprint)
        };
      }
      
      createFootprintBreakdownChart('footprint-breakdown-chart', footprintData);
    } catch (error) {
      console.error("Error setting up footprint breakdown chart:", error);
      // Create a simple fallback chart if there's an error
      const fallbackData = {
        'Commuting': data.latestFootprint.total_footprint * 0.4,
        'Office': data.latestFootprint.total_footprint * 0.4,
        'Travel': data.latestFootprint.total_footprint * 0.2
      };
      createFootprintBreakdownChart('footprint-breakdown-chart', fallbackData);
    }
  }
  
  // Initialize forecast chart if data is available
  if (data.forecastData && document.getElementById('forecast-chart')) {
    // Format forecast data for chart
    const chartData = formatForecastData(data.forecastData);
    createForecastChart('forecast-chart', chartData);
  }
  
  // Set up event listeners
  setupDashboardInteractions();
}

/**
 * Initialize the company dashboard
 * 
 * @param {Object} data - Dashboard data for the company view
 */
function initCompanyDashboard(data) {
  // Initialize department comparison chart
  if (data.departmentData && document.getElementById('department-chart')) {
    createDepartmentComparisonChart('department-chart', data.departmentData);
  }
  
  // Initialize trend chart
  if (data.trendData && document.getElementById('trend-chart')) {
    createCompanyTrendChart('trend-chart', data.trendData);
  }
  
  // Initialize forecast and savings charts
  if (data.forecastData && document.getElementById('company-forecast-chart')) {
    // Format forecast data for charts
    const chartData = formatForecastData(data.forecastData.chart_data);
    createForecastChart('company-forecast-chart', chartData);
    
    if (document.getElementById('savings-chart')) {
      createSavingsChart('savings-chart', chartData);
    }
  }
  
  // Set up event listeners
  setupCompanyDashboardInteractions();
}

/**
 * Calculate commute emissions from footprint data
 * 
 * @param {Object} footprint - Footprint data object
 * @return {number} - Commute emissions in kg CO2
 */
function calculateCommuteEmissions(footprint) {
  // This is a simplified calculation - the real one would be server-side
  const distance = footprint.commute_distance || 0;
  const mode = footprint.commute_mode || 'car';
  let factor = 0.41; // Default car factor
  
  // Adjust factor based on mode
  if (mode === 'bus') factor = 0.18;
  else if (mode === 'train') factor = 0.12;
  else if (mode === 'bike' || mode === 'walk') factor = 0;
  else if (mode === 'car') {
    if (footprint.car_type === 'electric') factor = 0.1;
    else if (footprint.car_type === 'hybrid') factor = 0.19;
  }
  
  // Weekly emissions (5 workdays)
  return parseFloat((distance * factor * 5).toFixed(2));
}

/**
 * Calculate diet emissions from footprint data
 * 
 * @param {Object} footprint - Footprint data object
 * @return {number} - Diet emissions in kg CO2
 */
function calculateDietEmissions(footprint) {
  // Simplified calculation
  const dietType = footprint.diet_type || 'omnivore';
  const localPercentage = footprint.local_food_percentage || 0;
  
  let baseFactor = 50; // Default omnivore factor
  
  if (dietType === 'pescatarian') baseFactor = 30;
  else if (dietType === 'vegetarian') baseFactor = 20;
  else if (dietType === 'vegan') baseFactor = 10;
  
  // Adjust for local food (up to 20% reduction)
  const localAdjustment = 1 - (localPercentage / 100 * 0.2);
  
  return parseFloat((baseFactor * localAdjustment).toFixed(2));
}

/**
 * Calculate office emissions from footprint data
 * 
 * @param {Object} footprint - Footprint data object
 * @return {number} - Office emissions in kg CO2
 */
function calculateOfficeEmissions(footprint) {
  // Simplified calculation
  const officeDays = footprint.office_days_per_week || 0;
  const paperUsage = footprint.paper_usage || 'medium';
  const energyUsage = footprint.energy_usage || 'medium';
  
  // Default factors
  let paperFactor = 2; // medium
  let energyFactor = 15; // medium
  
  if (paperUsage === 'low') paperFactor = 0.5;
  else if (paperUsage === 'high') paperFactor = 5;
  
  if (energyUsage === 'low') energyFactor = 5;
  else if (energyUsage === 'high') energyFactor = 30;
  
  // Scale by number of days in office
  const scaleFactor = officeDays / 5;
  
  return parseFloat(((paperFactor + energyFactor) * scaleFactor).toFixed(2));
}

/**
 * Format forecast data for chart display
 * 
 * @param {Object} forecastData - Raw forecast data
 * @return {Object} - Formatted data for charts
 */
function formatForecastData(forecastData) {
  // Handle different potential data structures
  if (forecastData.forecast) {
    // Format from API response
    return {
      labels: forecastData.forecast.map(item => `${item.month}/${item.year}`),
      baseline: forecastData.forecast.map(item => item.baseline),
      forecast: forecastData.forecast.map(item => item.emissions),
      savings: forecastData.forecast.map(item => item.savings)
    };
  } else {
    // Already in chart format
    return forecastData;
  }
}

/**
 * Set up event listeners and interactive elements for employee dashboard
 */
function setupDashboardInteractions() {
  // Toggle recommendation details
  const recommendationCards = document.querySelectorAll('.recommendation-card');
  recommendationCards.forEach(card => {
    const header = card.querySelector('.recommendation-header');
    const content = card.querySelector('.recommendation-content');
    
    if (header && content) {
      header.addEventListener('click', () => {
        content.classList.toggle('collapsed');
        header.classList.toggle('expanded');
      });
    }
  });
  
  // Handle refresh data button
  const refreshBtn = document.getElementById('refresh-data');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', function() {
      window.location.reload();
    });
  }
  
  // Handle forecast period selector
  const forecastSelector = document.getElementById('forecast-period');
  if (forecastSelector) {
    forecastSelector.addEventListener('change', function() {
      // In a real app, this would update the forecast data via AJAX
      // For now, just show a message
      showToast('Forecast period updated', 'info');
    });
  }
}

/**
 * Set up event listeners and interactive elements for company dashboard
 */
function setupCompanyDashboardInteractions() {
  // Handle department filter
  const deptFilter = document.getElementById('department-filter');
  if (deptFilter) {
    deptFilter.addEventListener('change', function() {
      // This would filter data in a real app
      showToast('Department filter applied', 'info');
    });
  }
  
  // Handle date range picker
  const dateRange = document.getElementById('date-range');
  if (dateRange) {
    dateRange.addEventListener('change', function() {
      showToast('Date range updated', 'info');
    });
  }
  
  // Toggle goal details
  const goalItems = document.querySelectorAll('.goal-item');
  goalItems.forEach(item => {
    const header = item.querySelector('.goal-header');
    const details = item.querySelector('.goal-details');
    
    if (header && details) {
      header.addEventListener('click', () => {
        details.classList.toggle('collapsed');
      });
    }
  });
}

/**
 * Show a toast notification
 * 
 * @param {string} message - Message to display
 * @param {string} type - Type of notification (info, success, error)
 */
function showToast(message, type = 'info') {
  // Create toast element
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  
  // Add to document
  document.body.appendChild(toast);
  
  // Trigger animation
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);
  
  // Remove after delay
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}
