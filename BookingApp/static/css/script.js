// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    });
});

// Animation on scroll
window.addEventListener('scroll', function() {
    const packages = document.querySelectorAll('.package-card');
    packages.forEach(package => {
        const packagePosition = package.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (packagePosition < screenPosition) {
            package.style.opacity = '1';
            package.style.transform = 'translateY(0)';
        }
    });
}); 