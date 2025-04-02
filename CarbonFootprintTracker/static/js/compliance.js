/**
 * Compliance Dashboard functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize compliance dashboard
    initComplianceDashboard();
});

/**
 * Initialize compliance dashboard with dynamic data
 */
function initComplianceDashboard() {
    // Set up period selector
    const periodSelector = document.getElementById('compliance-period');
    if (periodSelector) {
        periodSelector.addEventListener('change', function() {
            updateComplianceData(this.value);
        });
    }
    
    // Add click handlers to standard cards for details view
    const detailButtons = document.querySelectorAll('.standard-actions .btn');
    detailButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const standardCard = this.closest('.standard-card');
            const standardName = standardCard.querySelector('h4').textContent;
            showStandardDetails(standardName);
        });
    });
}

/**
 * Update compliance data based on selected period
 * @param {string} period - Selected time period
 */
function updateComplianceData(period) {
    console.log(`Updating compliance data for period: ${period}`);
    
    // In a production app, this would make an AJAX call to fetch data
    // For demo purposes, we'll simply update the UI with simulated data
    
    let score, standardsMet, standardsAction;
    
    // Simulate different data for different periods
    switch(period) {
        case 'previous':
            score = 79;
            standardsMet = 11;
            standardsAction = 3;
            break;
        case 'three-year':
            // Show trend data
            score = 87;
            standardsMet = 13;
            standardsAction = 2;
            // Would ideally show a trend chart here
            break;
        default: // current
            score = 87;
            standardsMet = 13;
            standardsAction = 2;
    }
    
    // Update the metrics
    updateMetric('Overall Compliance Score', `${score}%`);
    updateMetric('Standards Met', standardsMet);
    updateMetric('Standards Requiring Action', standardsAction);
    
    // Update progress bars
    document.querySelector('.card:first-child .progress-bar').style.width = `${score}%`;
}

/**
 * Update a metric value in the UI
 * @param {string} label - The metric label to update
 * @param {string|number} value - The new value
 */
function updateMetric(label, value) {
    const metrics = document.querySelectorAll('.metric');
    
    metrics.forEach(metric => {
        const metricLabel = metric.querySelector('.metric-label');
        if (metricLabel && metricLabel.textContent === label) {
            const metricValue = metric.querySelector('.metric-value');
            if (metricValue) {
                metricValue.textContent = value;
            }
        }
    });
}

/**
 * Show detailed information for a compliance standard
 * @param {string} standardName - Name of the standard to show details for
 */
function showStandardDetails(standardName) {
    console.log(`Showing details for: ${standardName}`);
    
    // In a production app, this would:
    // 1. Fetch detailed data about the standard
    // 2. Open a modal or navigate to a details page
    
    // For demo purposes, we'll show an alert with the standard name
    alert(`Compliance Details for: ${standardName}\n\nIn a full implementation, this would show detailed requirements, current status, historical compliance data, and action items.`);
}

/**
 * Add new regulatory update to the news feed
 * @param {Object} newsItem - News item data
 */
function addRegulatoryUpdate(newsItem) {
    const newsFeed = document.querySelector('.news-feed');
    if (!newsFeed) return;
    
    const newsItemElement = document.createElement('div');
    newsItemElement.className = 'news-item';
    
    newsItemElement.innerHTML = `
        <div class="news-date">${newsItem.date}</div>
        <h4 class="news-title">${newsItem.title}</h4>
        <p class="news-excerpt">${newsItem.excerpt}</p>
        <div class="news-tag">${newsItem.tag}</div>
    `;
    
    // Add to the beginning of the feed
    newsFeed.insertBefore(newsItemElement, newsFeed.firstChild);
}

/**
 * Update industry position data
 * @param {Object} positionData - Industry position data
 */
function updateIndustryPosition(positionData) {
    const positionMarker = document.querySelector('.marker-value');
    if (positionMarker) {
        positionMarker.textContent = positionData.position;
    }
    
    // Update comparison stats
    const comparisonItems = document.querySelectorAll('.comparison-item');
    comparisonItems.forEach(item => {
        const label = item.querySelector('.comparison-label').textContent;
        const value = item.querySelector('.comparison-value');
        const difference = item.querySelector('.comparison-difference');
        
        if (label === 'Industry Average Compliance' && positionData.averageCompliance) {
            value.textContent = `${positionData.averageCompliance}%`;
            updateComparisonDifference(difference, positionData.complianceDifference);
        } else if (label === 'Standards Met (Avg.)' && positionData.standardsMetAvg) {
            value.textContent = positionData.standardsMetAvg;
            updateComparisonDifference(difference, positionData.standardsMetDifference);
        } else if (label === 'Carbon Disclosure Score' && positionData.disclosureScore) {
            value.textContent = positionData.disclosureScore;
            difference.textContent = `Industry: ${positionData.industryDisclosureScore}`;
        }
    });
}

/**
 * Update comparison difference UI element
 * @param {Element} element - The difference element to update
 * @param {string|number} value - The new difference value
 */
function updateComparisonDifference(element, value) {
    if (!element) return;
    
    // Clear existing classes
    element.classList.remove('positive', 'negative', 'neutral');
    
    // Add appropriate class based on value
    if (value > 0) {
        element.classList.add('positive');
        element.textContent = `+${value}`;
    } else if (value < 0) {
        element.classList.add('negative');
        element.textContent = value; // already negative
    } else {
        element.classList.add('neutral');
        element.textContent = 'No change';
    }
}