/**
 * AI Test Generator - Core Client-Side Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // Show spinner on form submissions that generate tests
    const generatorForm = document.getElementById('generator-form');
    const loadingOverlay = document.getElementById('loading-overlay');

    if (generatorForm && loadingOverlay) {
        generatorForm.addEventListener('submit', (e) => {
            // Basic validation
            const subject = document.getElementById('subject');
            const topics = document.getElementById('topics');

            if (subject && !subject.value.trim()) {
                e.preventDefault();
                alert('Please enter a subject / Fan nomini kiriting.');
                subject.focus();
                return;
            }

            if (topics && !topics.value.trim()) {
                e.preventDefault();
                alert('Please enter topics / Mavzularni kiriting.');
                topics.focus();
                return;
            }

            // Show loading animation
            loadingOverlay.style.display = 'flex';
        });
    }
});
