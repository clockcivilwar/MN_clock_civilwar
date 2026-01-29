// Minnesota Civil War Clock - Main JavaScript

let currentData = null;
let allDatesData = {};
let availableDates = [];

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date selector and load all data
    initDateSelector();

    // Tab functionality for news section
    initNewsTabs();

    // Tab functionality for perspective section
    initPerspectiveTabs();
});

// Initialize date selector
function initDateSelector() {
    // Load available dates
    fetch('data/dates.json')
        .then(response => response.json())
        .then(data => {
            availableDates = data.available_dates.sort();
            const select = document.getElementById('date-select');
            if (!select) return;

            select.innerHTML = '';
            [...availableDates].reverse().forEach(date => {
                const option = document.createElement('option');
                option.value = date;
                option.textContent = formatDateLong(date);
                select.appendChild(option);
            });

            // Set to latest
            select.value = data.latest;

            // Add change listener
            select.addEventListener('change', function() {
                loadDateData(this.value);
                updateTrendChart(this.value);
            });

            // Load all dates data for the chart
            loadAllDatesData(data.latest);
        })
        .catch(err => {
            console.log('Using static date selector');
            // Fallback: load initial data
            const dateSelect = document.getElementById('date-select');
            if (dateSelect && dateSelect.value) {
                loadDateData(dateSelect.value);
            }
        });
}

// Load all dates data for trend chart
function loadAllDatesData(initialDate) {
    const promises = availableDates.map(date =>
        fetch(`data/${date}.json`)
            .then(response => response.json())
            .then(data => {
                allDatesData[date] = data;
                return data;
            })
            .catch(err => {
                console.error(`Error loading ${date}:`, err);
                return null;
            })
    );

    Promise.all(promises).then(() => {
        renderTrendChart();
        updateTrendChart(initialDate);
        loadDateData(initialDate);
    });
}

// Load data for a specific date
function loadDateData(date) {
    showLoading(true);

    fetch(`data/${date}.json`)
        .then(response => {
            if (!response.ok) throw new Error('Data not found');
            return response.json();
        })
        .then(data => {
            currentData = data;
            renderData(data);
            showLoading(false);
        })
        .catch(err => {
            console.error('Error loading data:', err);
            showLoading(false);
        });
}

// Render all data to page
function renderData(data) {
    // Get precise rating from analysis matrix averages
    let preciseRating = data.clock.rating;
    if (data.analysis && data.analysis.matrix && data.analysis.matrix.averages) {
        preciseRating = data.analysis.matrix.averages.overall;
    }

    // Update clock with precise rating
    updateClock(preciseRating, data.clock.status, data.clock.trend);

    // Update date display
    const analysisDate = document.getElementById('analysis-date');
    if (analysisDate) {
        analysisDate.textContent = formatDateLong(data.date);
    }

    // Update clock description
    const clockDesc = document.querySelector('.clock-meta .description');
    if (clockDesc) {
        clockDesc.textContent = data.clock.description;
    }

    // Update events section title
    const eventsTitle = document.querySelector('#events-section h2');
    if (eventsTitle) {
        eventsTitle.textContent = `Key Events - ${formatDateLong(data.date)}`;
    }

    // Update events list
    renderEvents(data.events);

    // Update news section
    renderNews(data.news);

    // Update analysis section
    renderAnalysis(data.analysis);

    // Update watch items
    renderWatch(data.watch);

    // Update scale active state
    updateScaleActive(data.clock.rating);
}

// Render events list
function renderEvents(events) {
    const list = document.getElementById('events-list');
    if (!list) return;

    list.innerHTML = events.map(event =>
        `<li><strong>${event.title}:</strong> ${event.description}</li>`
    ).join('');
}

// Render news section
function renderNews(news) {
    const sectionNote = document.querySelector('#news-section .section-note');
    if (sectionNote) {
        sectionNote.textContent = `${news.total_articles} articles extracted from ${news.total_sources} sources across the political spectrum`;
    }

    // Render MN Local
    renderNewsRegion('mn-local', news.minnesota_local);

    // Render US National
    renderNewsRegion('us-national', news.us_national);
}

function renderNewsRegion(containerId, regionData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const columns = ['left_leaning', 'centrist', 'right_leaning'];
    const labels = ['Left-Leaning', 'Centrist', 'Right-Leaning'];

    container.innerHTML = columns.map((col, idx) => {
        const sources = regionData[col] || [];
        const sourcesHtml = sources.map(source => `
            <div class="source-block">
                <h4>${source.name} <span class="article-count">${source.count} articles</span></h4>
                <ul class="article-list">
                    ${source.articles.map(article =>
                        `<li><a href="${article.url}" target="_blank" rel="noopener">${article.headline}</a></li>`
                    ).join('')}
                </ul>
            </div>
        `).join('');

        return `
            <div class="news-column">
                <h3>${labels[idx]}</h3>
                ${sourcesHtml}
            </div>
        `;
    }).join('');
}

// Render analysis section
function renderAnalysis(analysis) {
    // Update polarization note
    const polarNote = document.querySelector('.polarization-note');
    if (polarNote) {
        polarNote.innerHTML = `<strong>Polarization Index:</strong> ${analysis.polarization_index.toFixed(1)} points gap between Left (${analysis.matrix.averages.left.toFixed(2)}) and Right (${analysis.matrix.averages.right.toFixed(2)}) averages`;
    }

    // Update summary table
    renderSummaryTable(analysis.matrix);

    // Update perspective cards
    renderPerspectiveCards(analysis.perspectives);
}

function renderSummaryTable(matrix) {
    const tbody = document.querySelector('.summary-table tbody');
    if (!tbody) return;

    const rows = ['politician', 'news_analyst', 'legal_expert', 'finance_analyst'];
    const labels = ['Politician', 'News Analyst', 'Legal Expert', 'Finance Analyst'];

    tbody.innerHTML = rows.map((row, idx) => {
        const data = matrix[row];
        return `
            <tr>
                <td>${labels[idx]}</td>
                <td class="rating ${getRatingClass(data.left)}">${data.left}/12</td>
                <td class="rating ${getRatingClass(data.center)}">${data.center}/12</td>
                <td class="rating ${getRatingClass(data.right)}">${data.right}/12</td>
                <td>${data.avg.toFixed(1)}</td>
            </tr>
        `;
    }).join('') + `
        <tr class="total-row">
            <td><strong>Average</strong></td>
            <td><strong>${matrix.averages.left.toFixed(2)}</strong></td>
            <td><strong>${matrix.averages.center.toFixed(2)}</strong></td>
            <td><strong>${matrix.averages.right.toFixed(2)}</strong></td>
            <td><strong>${matrix.averages.overall.toFixed(2)}</strong></td>
        </tr>
    `;
}

function renderPerspectiveCards(perspectives) {
    const perspectiveMap = {
        'politician': 'politician',
        'news': 'news_analyst',
        'legal': 'legal_expert',
        'finance': 'finance_analyst'
    };

    Object.entries(perspectiveMap).forEach(([containerId, dataKey]) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        const data = perspectives[dataKey];
        const leanings = ['left', 'center', 'right'];
        const classes = ['left', 'center', 'right'];
        const labels = ['Left Wing', 'Centrist', 'Right Wing'];

        container.innerHTML = leanings.map((leaning, idx) => {
            const p = data[leaning];
            return `
                <div class="analysis-card ${classes[idx]}">
                    <div class="card-header">
                        <span class="leaning">${labels[idx]}</span>
                        <span class="rating-badge">${p.rating}/12</span>
                    </div>
                    <h4>${p.role}</h4>
                    <div class="card-body">
                        <p><strong>Assessment:</strong> "${p.summary}"</p>
                    </div>
                </div>
            `;
        }).join('');
    });
}

// Render watch items
function renderWatch(watch) {
    const escalateList = document.querySelector('.watch-item.escalate ul');
    const deescalateList = document.querySelector('.watch-item.deescalate ul');

    if (escalateList) {
        escalateList.innerHTML = watch.escalation.map(item => `<li>${item}</li>`).join('');
    }

    if (deescalateList) {
        deescalateList.innerHTML = watch.deescalation.map(item => `<li>${item}</li>`).join('');
    }
}

// Tab functionality
function initNewsTabs() {
    const newsTabs = document.querySelectorAll('.news-tabs .tab-btn');
    const newsContents = document.querySelectorAll('.news-content');

    newsTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetId = this.getAttribute('data-tab');
            newsTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            newsContents.forEach(content => {
                content.classList.toggle('hidden', content.id !== targetId);
            });
        });
    });
}

function initPerspectiveTabs() {
    const perspectiveTabs = document.querySelectorAll('.perspective-tabs .perspective-btn');
    const perspectiveContents = document.querySelectorAll('.perspective-content');

    perspectiveTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetId = this.getAttribute('data-perspective');
            perspectiveTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            perspectiveContents.forEach(content => {
                content.classList.toggle('hidden', content.id !== targetId);
            });
        });
    });
}

// Update clock display
function updateClock(rating, status, trend) {
    const clockValue = document.getElementById('clock-value');
    const clockStatus = document.getElementById('clock-status');
    const clockTrend = document.getElementById('clock-trend');

    if (clockStatus) {
        clockStatus.textContent = status;
        // Update status color class
        const levels = ['peaceful', 'elevated', 'high', 'severe', 'critical', 'midnight'];
        levels.forEach(level => clockStatus.classList.remove(`level-${level}`));
        clockStatus.classList.add(`level-${getSeverityLevel(rating)}`);
    }

    if (clockTrend) {
        clockTrend.textContent = trend;
        // Update trend class
        clockTrend.classList.remove('falling', 'stable');
        if (trend.toLowerCase().includes('fall') || trend.toLowerCase().includes('down') || trend.toLowerCase().includes('decreas')) {
            clockTrend.classList.add('falling');
        } else if (trend.toLowerCase().includes('stable') || trend.toLowerCase().includes('steady')) {
            clockTrend.classList.add('stable');
        }
    }

    if (clockValue) {
        clockValue.textContent = rating.toFixed(2);
        // Update value color
        clockValue.style.color = getTimerColor(rating);
    }

    // Update digital timer display
    updateDigitalTimer(rating);

    // Update analog clock
    updateAnalogClock(rating);
}

// Get severity level name from rating
function getSeverityLevel(rating) {
    if (rating >= 11) return 'midnight';
    if (rating >= 9) return 'critical';
    if (rating >= 7) return 'severe';
    if (rating >= 5) return 'high';
    if (rating >= 3) return 'elevated';
    return 'peaceful';
}

// Convert decimal rating to hours, minutes, seconds
function ratingToTime(rating) {
    // Rating is on 0-12 scale (like hours on a clock)
    const totalHours = rating;
    const hours = Math.floor(totalHours);
    const remainingMinutes = (totalHours - hours) * 60;
    const minutes = Math.floor(remainingMinutes);
    const seconds = Math.floor((remainingMinutes - minutes) * 60);

    return { hours, minutes, seconds };
}

// Update digital timer display
function updateDigitalTimer(rating) {
    const hoursEl = document.getElementById('timer-hours');
    const minutesEl = document.getElementById('timer-minutes');
    const secondsEl = document.getElementById('timer-seconds');

    if (!hoursEl || !minutesEl || !secondsEl) return;

    const time = ratingToTime(rating);

    hoursEl.textContent = String(time.hours).padStart(2, '0');
    minutesEl.textContent = String(time.minutes).padStart(2, '0');
    secondsEl.textContent = String(time.seconds).padStart(2, '0');

    // Color based on severity
    const color = getTimerColor(rating);
    hoursEl.style.color = color;
    minutesEl.style.color = color;
    secondsEl.style.color = color;
}

// Get color based on rating severity
function getTimerColor(rating) {
    if (rating >= 10) return '#922b21'; // Dark red - midnight approaching
    if (rating >= 8) return '#c0392b';  // Red - critical
    if (rating >= 6) return '#e67e22';  // Orange - severe/high
    if (rating >= 4) return '#f1c40f';  // Yellow - elevated
    return '#27ae60';                    // Green - peaceful
}

// Update analog clock display
function updateAnalogClock(rating) {
    const analogClock = document.getElementById('analog-clock');
    const handGroup = document.getElementById('clock-hand-group');
    const ratingArc = document.getElementById('rating-arc');
    const clockHand = document.getElementById('clock-hand');
    const clockCenter = analogClock ? analogClock.querySelector('.clock-center') : null;
    const clockCenterDot = analogClock ? analogClock.querySelector('.clock-center-dot') : null;

    if (!analogClock || !handGroup) return;

    // Calculate rotation angle
    // 12 o'clock = 0 degrees (top), increases clockwise
    // Rating 0 = 12 o'clock position, Rating 12 = back to 12 o'clock
    // For a clock: each hour = 30 degrees
    const angle = (rating / 12) * 360;
    handGroup.style.transform = `rotate(${angle}deg)`;

    // Get color for current rating
    const color = getSeverityColor(rating);

    // Update hand and center colors
    if (clockHand) clockHand.setAttribute('stroke', color);
    if (clockCenter) clockCenter.setAttribute('stroke', color);
    if (clockCenterDot) clockCenterDot.setAttribute('fill', color);

    // Update rating arc (shows progress around clock)
    if (ratingArc) {
        // Circumference of circle with r=85 is 2*PI*85 = 534.07
        const circumference = 2 * Math.PI * 85;
        const arcLength = (rating / 12) * circumference;
        ratingArc.setAttribute('stroke', color);
        ratingArc.setAttribute('stroke-dasharray', `${arcLength} ${circumference}`);
    }

    // Update severity level class for animations
    const levels = ['peaceful', 'elevated', 'high', 'severe', 'critical', 'midnight'];
    levels.forEach(level => analogClock.classList.remove(`level-${level}`));
    analogClock.classList.add(`level-${getSeverityLevel(rating)}`);
}

// Get color based on severity rating
function getSeverityColor(rating) {
    if (rating >= 11) return '#922b21'; // Midnight - darkest red
    if (rating >= 9) return '#c0392b';  // Critical - dark red
    if (rating >= 7) return '#e74c3c';  // Severe - red
    if (rating >= 5) return '#e67e22';  // High - orange
    if (rating >= 3) return '#f1c40f';  // Elevated - yellow
    return '#27ae60';                    // Peaceful - green
}

// Update scale active state
function updateScaleActive(rating) {
    const scaleItems = document.querySelectorAll('.scale-item');
    scaleItems.forEach(item => {
        item.classList.remove('active');
        const range = item.querySelector('.scale-range').textContent;
        const [min, max] = range.split('-').map(Number);
        if (rating >= min && rating <= max) {
            item.classList.add('active');
        }
    });
}

// Utility functions
function formatDateLong(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString + 'T12:00:00').toLocaleDateString('en-US', options);
}

function getRatingClass(rating) {
    if (rating >= 8) return 'high';
    if (rating >= 5) return 'medium';
    return 'low';
}

function showLoading(show) {
    let overlay = document.querySelector('.loading-overlay');
    if (!overlay && show) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(overlay);
    }
    if (overlay) {
        overlay.classList.toggle('active', show);
    }
}

// Render trend chart
function renderTrendChart() {
    const pointsContainer = document.getElementById('trend-points');
    const trendLine = document.getElementById('trend-line');
    const trendLineLeft = document.getElementById('trend-line-left');
    const trendLineCenter = document.getElementById('trend-line-center');
    const trendLineRight = document.getElementById('trend-line-right');
    const tooltip = document.getElementById('chart-tooltip');

    if (!pointsContainer || !trendLine || availableDates.length === 0) return;

    // Chart dimensions (wider layout)
    const chartLeft = 45;
    const chartRight = 680;
    const chartTop = 20;
    const chartBottom = 220;
    const chartWidth = chartRight - chartLeft;
    const chartHeight = chartBottom - chartTop;

    // Calculate positions for all series
    const points = [];
    const leftPoints = [];
    const centerPoints = [];
    const rightPoints = [];
    const sortedDates = [...availableDates].sort();

    sortedDates.forEach((date, index) => {
        const data = allDatesData[date];
        if (!data) return;

        const avg = data.analysis && data.analysis.matrix && data.analysis.matrix.averages;

        // Use precise rating from analysis matrix
        let rating = data.clock.rating;
        if (avg) {
            rating = avg.overall;
        }

        // X position: spread points evenly
        let x;
        if (sortedDates.length === 1) {
            x = chartLeft + chartWidth / 2;
        } else {
            x = chartLeft + (index / (sortedDates.length - 1)) * chartWidth;
        }

        // Y position: 12 at top (chartTop), 0 at bottom (chartBottom)
        const y = chartBottom - (rating / 12) * chartHeight;

        points.push({ date, rating, x, y });

        // Left/Center/Right series
        if (avg) {
            const leftRating = avg.left || 0;
            const centerRating = avg.center || 0;
            const rightRating = avg.right || 0;
            leftPoints.push({ x, y: chartBottom - (leftRating / 12) * chartHeight });
            centerPoints.push({ x, y: chartBottom - (centerRating / 12) * chartHeight });
            rightPoints.push({ x, y: chartBottom - (rightRating / 12) * chartHeight });
        }
    });

    // Draw left/center/right trend lines
    if (trendLineLeft && leftPoints.length > 0) {
        trendLineLeft.setAttribute('points', leftPoints.map(p => `${p.x},${p.y}`).join(' '));
    }
    if (trendLineCenter && centerPoints.length > 0) {
        trendLineCenter.setAttribute('points', centerPoints.map(p => `${p.x},${p.y}`).join(' '));
    }
    if (trendLineRight && rightPoints.length > 0) {
        trendLineRight.setAttribute('points', rightPoints.map(p => `${p.x},${p.y}`).join(' '));
    }

    // Draw overall trend line
    const linePoints = points.map(p => `${p.x},${p.y}`).join(' ');
    trendLine.setAttribute('points', linePoints);

    // Draw data points (overall only)
    pointsContainer.innerHTML = '';

    points.forEach(point => {
        // Create circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', point.x);
        circle.setAttribute('cy', point.y);
        circle.setAttribute('r', 5);
        circle.setAttribute('class', 'data-point');
        circle.setAttribute('data-date', point.date);
        circle.setAttribute('data-rating', point.rating);

        // Click handler
        circle.addEventListener('click', function() {
            const date = this.getAttribute('data-date');
            const select = document.getElementById('date-select');
            if (select) {
                select.value = date;
            }
            loadDateData(date);
            updateTrendChart(date);
        });

        // Hover handlers
        circle.addEventListener('mouseenter', function(e) {
            const date = this.getAttribute('data-date');
            const ratingVal = parseFloat(this.getAttribute('data-rating'));
            const data = allDatesData[date];
            const avg = data && data.analysis && data.analysis.matrix && data.analysis.matrix.averages;
            let text = `${formatDateShort(date)}: ${ratingVal.toFixed(2)}`;
            if (avg) {
                text += ` (L:${avg.left.toFixed(1)} C:${avg.center.toFixed(1)} R:${avg.right.toFixed(1)})`;
            }
            tooltip.textContent = text;
            tooltip.classList.add('visible');

            // Position tooltip relative to SVG
            const svgRect = document.getElementById('trend-chart').getBoundingClientRect();
            const containerRect = document.querySelector('.trend-chart-container').getBoundingClientRect();
            const scaleX = svgRect.width / 700;
            const scaleY = svgRect.height / 280;
            tooltip.style.left = (point.x * scaleX) + 'px';
            tooltip.style.top = (point.y * scaleY - 30) + 'px';
        });

        circle.addEventListener('mouseleave', function() {
            tooltip.classList.remove('visible');
        });

        pointsContainer.appendChild(circle);

        // Add date label for select dates (avoid clutter with many dates)
        if (sortedDates.length <= 14 || index % Math.ceil(sortedDates.length / 14) === 0 || index === sortedDates.length - 1) {
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', point.x);
            label.setAttribute('y', chartBottom + 15);
            label.setAttribute('class', 'point-label');
            label.textContent = formatDateShort(point.date);
            pointsContainer.appendChild(label);
        }
    });
}

// Update trend chart active state
function updateTrendChart(activeDate) {
    const points = document.querySelectorAll('#trend-points .data-point');
    points.forEach(point => {
        if (point.getAttribute('data-date') === activeDate) {
            point.classList.add('active');
        } else {
            point.classList.remove('active');
        }
    });
}

// Format date for chart labels
function formatDateShort(dateString) {
    const date = new Date(dateString + 'T12:00:00');
    return `${date.getMonth() + 1}/${date.getDate()}`;
}
