// Initialize Vanta.js Fog effect
VANTA.FOG({
    el: document.querySelector('body > div'),
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.00,
    minWidth: 200.00,
    speed: 2.00,
    zoom: 0.10
});

// Mobile navbar toggle functionality
const toggleButton = document.getElementById('navbar-toggle');
const mobileMenu = document.getElementById('mobile-menu');

toggleButton.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
});
