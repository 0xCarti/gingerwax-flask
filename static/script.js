let currentIndex = 0;

function showSlide(index) {
    const carousel = document.querySelector('.carousel');
    const totalSlides = document.querySelectorAll('.carousel-item').length;
    const description = document.getElementById('carousel-description');

    if (index >= totalSlides) {
        currentIndex = 0;
    } else if (index < 0) {
        currentIndex = totalSlides - 1;
    } else {
        currentIndex = index;
    }

    const offset = -currentIndex * 100;
    carousel.style.transform = `translateX(${offset}%)`;
    const currentImage = document.querySelectorAll('.carousel-item img')[currentIndex];
    description.textContent = currentImage.getAttribute('data-description');
}

function nextSlide() {
    showSlide(currentIndex + 1);
}

function prevSlide() {
    showSlide(currentIndex - 1);
}

// Automatically move to the next slide every 5 seconds
setInterval(nextSlide, 15000);

// Initial description
document.addEventListener('DOMContentLoaded', () => {
    const initialImage = document.querySelectorAll('.carousel-item img')[currentIndex];
    const description = document.getElementById('carousel-description');
    description.textContent = initialImage.getAttribute('data-description');
});

