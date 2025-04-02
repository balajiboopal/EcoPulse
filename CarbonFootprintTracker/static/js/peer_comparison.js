/**
 * Peer Comparison Visualization
 * 
 * This module provides interactive visualizations for comparing carbon footprints
 * between employees and departments.
 */

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Chart colors
    const visualColors = {
        personal: '#4e79a7',
        travel: '#f28e2c',
        office: '#e15759',
        transactions: '#76b7b2'
    };

    // Component expansion
    const components = document.querySelectorAll('.component');
    components.forEach(component => {
        component.addEventListener('click', function() {
            this.classList.toggle('expanded');
        });
    });
    
    // Visualization toggle
    const toggleButtons = document.querySelectorAll('.viz-toggle-btn');
    const chartContainers = document.querySelectorAll('.chart-viz');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const vizType = this.getAttribute('data-viz');
            
            // Update active button
            toggleButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide appropriate visualization
            chartContainers.forEach(container => {
                container.classList.remove('active');
                if (container.id === `${vizType}Chart` || container.id === 'breakdownChart' && vizType === 'doughnut') {
                    container.classList.add('active');
                }
            });

            // Redraw treemap when it becomes visible
            if (vizType === 'treemap') {
                setTimeout(createTreemap, 100);
            }
        });
    });

    // Extract the footprint data from the page
    const footprintData = {
        personal: parseFloat(document.getElementById('personal-footprint').value) || 0,
        travel: parseFloat(document.getElementById('travel-footprint').value) || 0,
        office: parseFloat(document.getElementById('office-footprint').value) || 0,
        transactions: parseFloat(document.getElementById('transactions-footprint').value) || 0
    };

    const hasTransactions = parseFloat(document.getElementById('transactions-footprint').value) > 0;
    
    // Format data for charts
    const labels = ['Personal', 'Business Travel', 'Office Usage'];
    if (hasTransactions) labels.push('Transactions');
    
    const dataValues = [
        footprintData.personal,
        footprintData.travel,
        footprintData.office
    ];
    if (hasTransactions) dataValues.push(footprintData.transactions);

    const colorValues = [
        visualColors.personal,
        visualColors.travel,
        visualColors.office
    ];
    if (hasTransactions) colorValues.push(visualColors.transactions);
    
    // Tree map data structure with subcategories
    const treeMapData = {
        name: 'Carbon Footprint',
        children: [
            { 
                name: 'Personal', 
                children: [
                    { name: 'Commute', value: footprintData.personal * 0.4, category: 'personal-commute' },
                    { name: 'Home', value: footprintData.personal * 0.35, category: 'personal-home' },
                    { name: 'Diet', value: footprintData.personal * 0.25, category: 'personal-diet' }
                ],
                category: 'personal'
            },
            { name: 'Business Travel', value: footprintData.travel, category: 'travel' },
            { 
                name: 'Office Usage', 
                children: [
                    { name: 'Electricity', value: footprintData.office * 0.5, category: 'office-electricity' },
                    { name: 'Equipment', value: footprintData.office * 0.3, category: 'office-equipment' },
                    { name: 'Supplies', value: footprintData.office * 0.2, category: 'office-supplies' }
                ],
                category: 'office'
            }
        ]
    };

    // Add transactions if available
    if (hasTransactions) {
        treeMapData.children.push({ 
            name: 'Transactions', 
            value: footprintData.transactions, 
            category: 'transactions' 
        });
    }
    
    // Create the doughnut chart
    const breakdownCtx = document.getElementById('breakdownChart').getContext('2d');
    const doughnutChart = new Chart(breakdownCtx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: dataValues,
                backgroundColor: colorValues,
                borderColor: 'rgba(255, 255, 255, 0.5)',
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            family: 'Inter, sans-serif',
                            size: 14
                        },
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total * 100) * 10) / 10;
                            return `${context.label}: ${value.toFixed(1)} kg (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutBounce'
            }
        }
    });
    
    // Create the bar chart
    const barCtx = document.getElementById('barChart').getContext('2d');
    const barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Carbon Footprint (kg CO₂)',
                data: dataValues,
                backgroundColor: colorValues,
                borderColor: 'rgba(255, 255, 255, 0.5)',
                borderWidth: 1,
                borderRadius: 4,
                barThickness: 45
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = dataValues.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total * 100) * 10) / 10;
                            return `${value.toFixed(1)} kg (${percentage}%)`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'kg CO₂'
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
    
    // Create the treemap
    function createTreemap() {
        const container = document.getElementById('treemapChart');
        if (!container) return;

        const width = container.offsetWidth;
        const height = 350;
        
        // Clear any existing SVG
        d3.select('#treemapChart').selectAll('svg').remove();
        
        // Create SVG
        const svg = d3.select('#treemapChart')
            .append('svg')
            .attr('width', width)
            .attr('height', height);
            
        // Hierarchy and treemap layout
        const root = d3.hierarchy(treeMapData)
            .sum(d => d.value)
            .sort((a, b) => b.value - a.value);
            
        const treemapLayout = d3.treemap()
            .size([width, height])
            .paddingOuter(10)
            .paddingInner(3)
            .round(true);
            
        treemapLayout(root);
        
        // Calculate percentage for each category
        const totalValue = dataValues.reduce((a, b) => a + b, 0);
        
        // Create treemap cells
        const cells = svg.selectAll('g')
            .data(root.leaves())
            .enter()
            .append('g')
            .attr('transform', d => `translate(${d.x0},${d.y0})`)
            .attr('class', d => {
                // Add both the specific subcategory class and the main category class
                const mainCategory = d.data.category.split('-')[0];
                return `treemap-cell ${d.data.category} ${mainCategory}`;
            })
            .on('mouseover', function(event, d) {
                // Highlight this category across all visualizations
                highlightCategory(d.data.category);
            })
            .on('mouseout', function() {
                // Remove highlight
                removeHighlight();
            })
            .on('click', function(event, d) {
                // Show detailed info for this category
                showCategoryDetails(d.data.category);
            });
            
        // Add rectangles
        cells.append('rect')
            .attr('width', d => Math.max(0, d.x1 - d.x0))
            .attr('height', d => Math.max(0, d.y1 - d.y0))
            .attr('fill', d => {
                // Extract the main category from subcategories (e.g., 'personal-commute' -> 'personal')
                const mainCategory = d.data.category.split('-')[0];
                
                // Color subcategories based on the main category with slight variations
                switch(mainCategory) {
                    case 'personal':
                        // For personal subcategories, use different shades of the personal color
                        if (d.data.category === 'personal-commute') return visualColors.personal;
                        if (d.data.category === 'personal-home') return d3.color(visualColors.personal).brighter(0.5);
                        if (d.data.category === 'personal-diet') return d3.color(visualColors.personal).darker(0.5);
                        return visualColors.personal;
                        
                    case 'travel': 
                        return visualColors.travel;
                        
                    case 'office':
                        // For office subcategories, use different shades of the office color
                        if (d.data.category === 'office-electricity') return visualColors.office;
                        if (d.data.category === 'office-equipment') return d3.color(visualColors.office).brighter(0.5);
                        if (d.data.category === 'office-supplies') return d3.color(visualColors.office).darker(0.5);
                        return visualColors.office;
                        
                    case 'transactions': 
                        return visualColors.transactions;
                        
                    default: 
                        return '#ccc';
                }
            })
            .attr('stroke', '#fff')
            .attr('rx', 4)
            .attr('ry', 4);
            
        // Add category labels
        cells.append('text')
            .attr('x', 5)
            .attr('y', 20)
            .attr('fill', '#fff')
            .style('font-weight', 'bold')
            .style('font-size', '14px')
            .text(d => {
                // Only show text if cell is big enough
                const cellWidth = d.x1 - d.x0;
                const cellHeight = d.y1 - d.y0;
                
                if (cellWidth < 30 || cellHeight < 30) return '';
                return d.data.name;
            });
            
        // Add value labels
        cells.append('text')
            .attr('x', 5)
            .attr('y', 40)
            .attr('fill', '#fff')
            .style('font-size', '12px')
            .text(d => {
                // Only show text if cell is big enough
                const cellWidth = d.x1 - d.x0;
                const cellHeight = d.y1 - d.y0;
                
                if (cellWidth < 60 || cellHeight < 50) return '';
                return `${d.data.value.toFixed(1)} kg`;
            });
            
        // Add percentage labels
        cells.append('text')
            .attr('x', 5)
            .attr('y', 60)
            .attr('fill', '#fff')
            .style('font-size', '12px')
            .text(d => {
                // Only show text if cell is big enough
                const cellWidth = d.x1 - d.x0;
                const cellHeight = d.y1 - d.y0;
                
                if (cellWidth < 60 || cellHeight < 50) return '';
                const percentage = Math.round((d.data.value / totalValue) * 100);
                return `${percentage}%`;
            });
    }
    
    // Create the initial treemap
    setTimeout(createTreemap, 100);
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (document.getElementById('treemapChart').classList.contains('active')) {
            createTreemap();
        }
    });
    
    // Handle component interactions
    document.querySelectorAll('.interactive-component').forEach(component => {
        component.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            showCategoryDetails(category);
        });
        
        component.addEventListener('mouseover', function() {
            const category = this.getAttribute('data-category');
            highlightCategory(category);
        });
        
        component.addEventListener('mouseout', function() {
            removeHighlight();
        });
    });
    
    // Function to highlight a category across all visualizations
    function highlightCategory(category) {
        // Get main category if this is a subcategory (e.g., 'personal-commute' -> 'personal')
        const mainCategory = category.split('-')[0];
        
        // Highlight component - only highlight the main category in the components panel
        document.querySelectorAll('.interactive-component').forEach(comp => {
            if (comp.getAttribute('data-category') === mainCategory) {
                comp.classList.add('highlighted');
            } else {
                comp.classList.add('dimmed');
            }
        });
        
        // For treemap, highlight the exact subcategory or all cells of a main category
        document.querySelectorAll('.treemap-cell').forEach(cell => {
            if (cell.classList.contains(category) || 
                (category.indexOf('-') === -1 && cell.classList.contains(category))) {
                cell.classList.add('highlighted');
            } else {
                cell.classList.add('dimmed');
            }
        });
    }
    
    // Function to remove all highlights
    function removeHighlight() {
        document.querySelectorAll('.interactive-component, .treemap-cell').forEach(el => {
            el.classList.remove('highlighted');
            el.classList.remove('dimmed');
        });
    }
    
    // Function to show detailed information about a category
    function showCategoryDetails(category) {
        // Get main category if this is a subcategory
        const mainCategory = category.split('-')[0];
        
        // Find the component and expand it
        const component = document.querySelector(`.component.${mainCategory}`);
        if (component) {
            component.classList.add('expanded');
        }
    }
});