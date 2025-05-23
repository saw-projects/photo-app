document.addEventListener('DOMContentLoaded', function() {
    // Variables
    const slideshow = document.getElementById('slideshow');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    
    let slides = document.querySelectorAll('.slide');
    let currentSlide = 0;
    let isPlaying = false;
    let slideInterval;
    const intervalTime = 5000; // 5 seconds
    
    // Load photos from server on page load
    loadPhotosFromServer();

    // Functions
    function showSlide(n) {
        slides.forEach(slide => slide.classList.remove('active'));
        currentSlide = (n + slides.length) % slides.length;
        slides[currentSlide].classList.add('active');
    }

    function nextSlide() {
        showSlide(currentSlide + 1);
    }

    function prevSlide() {
        showSlide(currentSlide - 1);
    }

    function togglePlayPause() {
        if (isPlaying) {
            clearInterval(slideInterval);
            playPauseBtn.textContent = '▶';
        } else {
            slideInterval = setInterval(nextSlide, intervalTime);
            playPauseBtn.textContent = '⏸';
        }
        isPlaying = !isPlaying;
    }

    // Function to load photos from the server
    function loadPhotosFromServer() {
        fetch('/photos')
            .then(response => response.json())
            .then(photoUrls => {
                if (photoUrls.length > 0) {
                    // Clear placeholder if it exists
                    slideshow.innerHTML = '';
                    slides = [];
                    
                    // Add each photo from the server
                    photoUrls.forEach((photoUrl, index) => {
                        const slide = document.createElement('div');
                        slide.className = 'slide';
                        if (index === 0) slide.classList.add('active');
                        slide.innerHTML = `<img src="${photoUrl}" alt="Photo ${index + 1}">`;
                        slideshow.appendChild(slide);
                    });
                    
                    // Update slides array
                    slides = document.querySelectorAll('.slide');
                    currentSlide = 0;
                }
            })
            .catch(error => console.error('Error loading photos:', error));
    }

    function handleFileSelect(event) {
        const files = event.target.files;
        if (files.length === 0) return;
        
        // Upload each file to the server
        Array.from(files).forEach(file => {
            if (!file.type.match('image.*')) return;
            
            const formData = new FormData();
            formData.append('photo', file);
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('File uploaded successfully:', data.filename);
                    // Reload all photos from server after upload
                    loadPhotosFromServer();
                } else {
                    console.error('Upload error:', data.error);
                }
            })
            .catch(error => {
                console.error('Upload failed:', error);
            });
        });
    }

    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.log(`Error attempting to enable fullscreen: ${err.message}`);
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

    // Event listeners
    prevBtn.addEventListener('click', function() {
        prevSlide();
        if (isPlaying) {
            clearInterval(slideInterval);
            slideInterval = setInterval(nextSlide, intervalTime);
        }
    });

    nextBtn.addEventListener('click', function() {
        nextSlide();
        if (isPlaying) {
            clearInterval(slideInterval);
            slideInterval = setInterval(nextSlide, intervalTime);
        }
    });

    playPauseBtn.addEventListener('click', togglePlayPause);
    
    uploadBtn.addEventListener('click', function() {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', handleFileSelect);
    
    fullscreenBtn.addEventListener('click', toggleFullscreen);

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            prevSlide();
        } else if (e.key === 'ArrowRight') {
            nextSlide();
        } else if (e.key === ' ') {
            togglePlayPause();
        } else if (e.key === 'f') {
            toggleFullscreen();
        }
    });
});
