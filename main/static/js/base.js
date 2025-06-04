// This is the content for your base.js file

// Theme Toggle Logic
const themeToggleBtn = document.getElementById('theme-toggle');
const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');
const htmlElement = document.documentElement;

// Set initial theme based on localStorage or system preference
const currentTheme = localStorage.getItem('color-theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

if (currentTheme === 'dark' || (!currentTheme && prefersDark)) {
  htmlElement.classList.add('dark');
  themeToggleDarkIcon.classList.add('hidden'); // Hide dark icon
  themeToggleLightIcon.classList.remove('hidden'); // Show light icon
} else {
  htmlElement.classList.remove('dark');
  themeToggleDarkIcon.classList.remove('hidden'); // Show dark icon
  themeToggleLightIcon.classList.add('hidden'); // Hide light icon
}

// Event listener for theme toggle button
themeToggleBtn.addEventListener('click', () => {
  // Toggle icons visibility
  themeToggleDarkIcon.classList.toggle('hidden');
  themeToggleLightIcon.classList.toggle('hidden');

  // Toggle 'dark' class on HTML element and update localStorage
  if (htmlElement.classList.contains('dark')) {
    htmlElement.classList.remove('dark');
    localStorage.setItem('color-theme', 'light');
  } else {
    htmlElement.classList.add('dark');
    localStorage.setItem('color-theme', 'dark');
  }
});

// Mobile Menu Toggle Logic
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');

mobileMenuButton.addEventListener('click', () => {
  mobileMenu.classList.toggle('hidden');
  // Toggle aria-expanded for accessibility
  const isExpanded = mobileMenuButton.getAttribute('aria-expanded') === 'true';
  mobileMenuButton.setAttribute('aria-expanded', !isExpanded);
});