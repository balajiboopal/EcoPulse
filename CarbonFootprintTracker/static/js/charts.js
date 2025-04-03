/**
 * Charts and data visualization for Carbon Footprint Tracker
 * 
 * This module provides chart creation and management functionality using Chart.js
 */

// Chart color palette matching our design
const chartColors = {
  primary: '#2ECC71',
  secondary: '#3498DB',
  warning: '#F1C40F',
  danger: '#E74C3C',
  light: '#F9FAFB',
  dark: '#2C3E50',
  gray: '#95A5A6',
  
  // Company palette
  companyPrimary: '#34A853',
  companySecondary: '#4285F4',
  companyWarning: '#FBBC05',
  companyDanger: '#EA4335',
  
  // Transparent versions
  primaryAlpha: 'rgba(46, 204, 113, 0.2)',
  secondaryAlpha: 'rgba(52, 152, 219, 0.2)',
  warningAlpha: 'rgba(241, 196, 15, 0.2)',
  dangerAlpha: 'rgba(231, 76, 60, 0.2)'
};

/**
 * Create a line chart for historical carbon footprint data
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Array of date labels
 * @param {Array} scores - Array of footprint scores
 * @param {Array} emissions - Array of emissions data
 */
function createFootprintHistoryChart(canvasId, labels, scores, emissions) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  // Create the chart
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Carbon Score',
          data: scores,
          borderColor: chartColors.primary,
          backgroundColor: chartColors.primaryAlpha,
          borderWidth: 2,
          tension: 0.2,
          yAxisID: 'y'
        },
        {
          label: 'Emissions (kg CO₂)',
          data: emissions,
          borderColor: chartColors.secondary,
          backgroundColor: chartColors.secondaryAlpha,
          borderWidth: 2,
          tension: 0.2,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y: {
          position: 'left',
          title: {
            display: true,
            text: 'Score (higher is better)'
          },
          suggestedMin: 0,
          suggestedMax: 100,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y1: {
          position: 'right',
          title: {
            display: true,
            text: 'kg CO₂'
          },
          grid: {
            drawOnChartArea: false
          }
        }
      },
      plugins: {
        tooltip: {
          mode: 'index',
          intersect: false
        },
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 20
          }
        }
      }
    }
  });
}

/**
 * Charts and data visualization for Carbon Footprint Tracker
 * 
 * This module provides chart creation and management functionality using Chart.js
 */

// Chart color palette matching our design


/**
 * Create a demo chart for showcasing carbon emissions and sustainability scores
 * 
 * @param {string} canvasId - The ID of the canvas element
 */
function createDemoChart(canvasId) {
  const ctx = document.getElementById(canvasId).getContext('2d');

  // Dummy data for the demo
  const labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July'];
  const emissions = [120, 100, 90, 80, 70, 60, 50]; // Carbon emissions in kg CO₂
  const scores = [50, 60, 70, 75, 80, 85, 90]; // Sustainability scores

  // Create the chart
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels, // X-axis labels
      datasets: [
        {
          label: 'Carbon Emissions (kg CO₂)',
          data: emissions, // Y-axis data for emissions
          borderColor: chartColors.danger, // Line color
          backgroundColor: chartColors.dangerAlpha, // Fill color
          borderWidth: 2,
          tension: 0.3, // Smooth curve
          yAxisID: 'y'
        },
        {
          label: 'Sustainability Score',
          data: scores, // Y-axis data for scores
          borderColor: chartColors.primary, // Line color
          backgroundColor: chartColors.primaryAlpha, // Fill color
          borderWidth: 2,
          tension: 0.3, // Smooth curve
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Months'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y: {
          position: 'left',
          title: {
            display: true,
            text: 'Carbon Emissions (kg CO₂)'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y1: {
          position: 'right',
          title: {
            display: true,
            text: 'Sustainability Score'
          },
          min: 0,
          max: 100,
          grid: {
            drawOnChartArea: false // Don't overlap grids
          }
        }
      },
      plugins: {
        legend: {
          position: 'top'
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      }
    }
  });
}
/**
 * Create a doughnut chart for footprint breakdown
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} footprintData - Footprint breakdown data
 */
function createFootprintBreakdownChart(canvasId, footprintData) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  // Process data for chart
  const labels = Object.keys(footprintData);
  const values = Object.values(footprintData);
  const colors = [
    chartColors.primary,
    chartColors.secondary,
    chartColors.warning
  ];
  
  // Create the chart
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderColor: chartColors.light,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 20
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.raw || 0;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = Math.round((value / total) * 100);
              return `${label}: ${value.toFixed(1)} kg CO₂ (${percentage}%)`;
            }
          }
        }
      },
      cutout: '70%'
    }
  });
}

/**
 * Create a forecast chart showing projected emissions
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} forecastData - Forecast data containing labels and datasets
 */
function createSavingsChart(canvasId) {
  const ctx = document.getElementById(canvasId).getContext('2d');

  // Hardcoded data for the demo
  const labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July'];
  const savingsData = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]; // Monthly Savings

  // Create the chart
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels, // X-axis labels
      datasets: [
        {
          label: 'kg CO₂ Saved',
          data: savingsData,
          backgroundColor: 'rgba(54, 162, 235, 0.5)', // Bar color
          borderColor: 'rgba(54, 162, 235, 1)', // Border color
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Months',
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)',
          },
        },
        y: {
          title: {
            display: true,
            text: 'kg CO₂ Saved',
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)',
          },
        },
      },
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        },
      },
    },
  });
}

/**
 * Create a bar chart for department comparison
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} departmentData - Data for different departments
 */
function createDepartmentComparisonChart(canvasId, departmentData) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  // Process data for chart
  const departments = Object.keys(departmentData);
  const emissions = departments.map(dept => departmentData[dept].avg_emissions || 0);
  const scores = departments.map(dept => departmentData[dept].avg_score || 0);
  
  // Create the chart
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: departments,
      datasets: [
        {
          label: 'Avg. Emissions (kg CO₂)',
          data: emissions,
          backgroundColor: chartColors.companySecondary,
          yAxisID: 'y'
        },
        {
          label: 'Avg. Score',
          data: scores,
          backgroundColor: chartColors.companyPrimary,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: {
            display: false
          }
        },
        y: {
          position: 'left',
          title: {
            display: true,
            text: 'kg CO₂'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y1: {
          position: 'right',
          title: {
            display: true,
            text: 'Score'
          },
          min: 0,
          max: 100,
          grid: {
            drawOnChartArea: false
          }
        }
      },
      plugins: {
        legend: {
          position: 'top'
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      }
    }
  });
}

/**
 * Create a line chart for company-wide trend data
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} trendData - Monthly trend data
 */
function createCompanyTrendChart(canvasId, trendData) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  // Process data for chart
  const labels = trendData.map(item => item.month);
  const emissions = trendData.map(item => item.emissions);
  const scores = trendData.map(item => item.score);
  
  // Create the chart
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Total Emissions (kg CO₂)',
          data: emissions,
          borderColor: chartColors.companySecondary,
          backgroundColor: 'rgba(66, 133, 244, 0.1)',
          borderWidth: 2,
          tension: 0.3,
          fill: true,
          yAxisID: 'y'
        },
        {
          label: 'Average Score',
          data: scores,
          borderColor: chartColors.companyPrimary,
          borderWidth: 2,
          tension: 0.3,
          fill: false,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y: {
          position: 'left',
          title: {
            display: true,
            text: 'kg CO₂'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y1: {
          position: 'right',
          title: {
            display: true,
            text: 'Score'
          },
          min: 0,
          max: 100,
          grid: {
            drawOnChartArea: false
          }
        }
      },
      plugins: {
        legend: {
          position: 'top'
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      }
    }
  });
}

/**
 * Create a savings comparison chart
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} forecastData - Forecast data with savings information
 */
function createSavingsChart(canvasId) {
  const ctx = document.getElementById(canvasId).getContext('2d');

  // Hardcoded data for the demo
  const labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July'];
  const savingsData = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]; // Monthly Savings

  // Create the chart
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels, // X-axis labels
      datasets: [
        {
          label: 'kg CO₂ Saved',
          data: savingsData,
          backgroundColor: 'rgba(54, 162, 235, 0.5)', // Bar color
          borderColor: 'rgba(54, 162, 235, 1)', // Border color
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Months',
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)',
          },
        },
        y: {
          title: {
            display: true,
            text: 'kg CO₂ Saved',
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)',
          },
        },
      },
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        },
      },
    },
  });
}
