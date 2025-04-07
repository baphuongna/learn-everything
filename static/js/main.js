// Main JavaScript for Learning Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
    
    // Study Session Timer
    const startTimerBtn = document.getElementById('start-timer');
    const pauseTimerBtn = document.getElementById('pause-timer');
    const resetTimerBtn = document.getElementById('reset-timer');
    const timerDisplay = document.getElementById('timer-display');
    
    if (startTimerBtn && pauseTimerBtn && resetTimerBtn && timerDisplay) {
        let seconds = 0;
        let minutes = 0;
        let hours = 0;
        let timerInterval;
        let isRunning = false;
        
        function updateTimerDisplay() {
            timerDisplay.textContent = 
                (hours < 10 ? '0' + hours : hours) + ':' +
                (minutes < 10 ? '0' + minutes : minutes) + ':' +
                (seconds < 10 ? '0' + seconds : seconds);
        }
        
        function incrementTimer() {
            seconds++;
            if (seconds >= 60) {
                seconds = 0;
                minutes++;
                if (minutes >= 60) {
                    minutes = 0;
                    hours++;
                }
            }
            updateTimerDisplay();
        }
        
        startTimerBtn.addEventListener('click', function() {
            if (!isRunning) {
                isRunning = true;
                timerInterval = setInterval(incrementTimer, 1000);
                startTimerBtn.classList.add('d-none');
                pauseTimerBtn.classList.remove('d-none');
            }
        });
        
        pauseTimerBtn.addEventListener('click', function() {
            if (isRunning) {
                isRunning = false;
                clearInterval(timerInterval);
                pauseTimerBtn.classList.add('d-none');
                startTimerBtn.classList.remove('d-none');
            }
        });
        
        resetTimerBtn.addEventListener('click', function() {
            isRunning = false;
            clearInterval(timerInterval);
            seconds = 0;
            minutes = 0;
            hours = 0;
            updateTimerDisplay();
            pauseTimerBtn.classList.add('d-none');
            startTimerBtn.classList.remove('d-none');
        });
    }
    
    // Flashcard Functionality
    const flashcards = document.querySelectorAll('.flashcard');
    
    flashcards.forEach(card => {
        card.addEventListener('click', function() {
            this.classList.toggle('flipped');
        });
    });
    
    // Quiz Timer
    const quizTimerElement = document.getElementById('quiz-timer');
    const quizForm = document.getElementById('quiz-form');
    
    if (quizTimerElement && quizForm) {
        const timeLimit = parseInt(quizTimerElement.dataset.timeLimit) * 60; // Convert to seconds
        let timeRemaining = timeLimit;
        
        const timerInterval = setInterval(function() {
            timeRemaining--;
            
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            
            quizTimerElement.textContent = 
                (minutes < 10 ? '0' + minutes : minutes) + ':' +
                (seconds < 10 ? '0' + seconds : seconds);
            
            if (timeRemaining <= 0) {
                clearInterval(timerInterval);
                alert('Hết thời gian! Bài làm của bạn sẽ được nộp tự động.');
                quizForm.submit();
            }
        }, 1000);
    }
    
    // Dark Mode Toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            
            // Save preference to localStorage
            if (document.body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');
            } else {
                localStorage.setItem('darkMode', 'disabled');
            }
        });
        
        // Check for saved preference
        if (localStorage.getItem('darkMode') === 'enabled') {
            document.body.classList.add('dark-mode');
        }
    }
    
    // Spaced Repetition Algorithm
    function calculateNextReviewDate(recallLevel) {
        const now = new Date();
        let nextDate = new Date();
        
        switch(parseInt(recallLevel)) {
            case 1: // Hard to remember
                nextDate.setDate(now.getDate() + 1); // Review tomorrow
                break;
            case 2: // Somewhat remember
                nextDate.setDate(now.getDate() + 3); // Review in 3 days
                break;
            case 3: // Easy to remember
                nextDate.setDate(now.getDate() + 7); // Review in 7 days
                break;
            default:
                nextDate.setDate(now.getDate() + 1);
        }
        
        return nextDate;
    }
    
    // Handle recall level buttons if they exist
    const recallButtons = document.querySelectorAll('.recall-btn');
    
    recallButtons.forEach(button => {
        button.addEventListener('click', function() {
            const recallLevel = this.dataset.level;
            const flashcardId = this.closest('.flashcard-container').dataset.id;
            const nextReviewDate = calculateNextReviewDate(recallLevel);
            
            // This would typically be sent to the server via AJAX
            console.log(`Flashcard ${flashcardId} recall level: ${recallLevel}, next review: ${nextReviewDate}`);
        });
    });
});
