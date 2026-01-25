// Minnesota Civil War Clock - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality for news section
    const newsTabs = document.querySelectorAll('.news-tabs .tab-btn');
    const newsContents = document.querySelectorAll('.news-content');

    newsTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetId = this.getAttribute('data-tab');

            // Update active tab
            newsTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // Show corresponding content
            newsContents.forEach(content => {
                if (content.id === targetId) {
                    content.classList.remove('hidden');
                } else {
                    content.classList.add('hidden');
                }
            });
        });
    });

    // Tab functionality for perspective section
    const perspectiveTabs = document.querySelectorAll('.perspective-tabs .perspective-btn');
    const perspectiveContents = document.querySelectorAll('.perspective-content');

    perspectiveTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetId = this.getAttribute('data-perspective');

            // Update active tab
            perspectiveTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // Show corresponding content
            perspectiveContents.forEach(content => {
                if (content.id === targetId) {
                    content.classList.remove('hidden');
                } else {
                    content.classList.add('hidden');
                }
            });
        });
    });

    // Animate clock hand on load
    animateClockHand(7); // Current rating is 7/12
});

// Animate clock hand to position
function animateClockHand(rating) {
    const clockHand = document.getElementById('clock-hand');
    if (!clockHand) return;

    // Calculate rotation: 0 = 6 o'clock (180deg), 12 = 12 o'clock (0deg)
    // Each hour = 30 degrees
    // Rating 7 = 7 * 30 = 210 degrees from 12 o'clock
    const rotation = (rating / 12) * 360;

    // Start from 0 and animate to target
    clockHand.style.transition = 'none';
    clockHand.style.transform = 'translateX(-50%) rotate(0deg)';

    // Force reflow
    clockHand.offsetHeight;

    // Animate to target position
    clockHand.style.transition = 'transform 2s ease-out';
    clockHand.style.transform = `translateX(-50%) rotate(${rotation}deg)`;
}

// Update clock display
function updateClock(rating, status, trend) {
    const clockValue = document.getElementById('clock-value');
    const clockStatus = document.getElementById('clock-status');
    const clockTrend = document.getElementById('clock-trend');

    if (clockValue) clockValue.textContent = rating;
    if (clockStatus) clockStatus.textContent = status;
    if (clockTrend) clockTrend.textContent = trend;

    animateClockHand(rating);

    // Update scale active item
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

// Utility: Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}
