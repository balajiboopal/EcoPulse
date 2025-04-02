/**
 * Quiz functionality for Carbon Footprint Tracker
 * 
 * Handles quiz interaction, validation, and submission
 */

// Store the current quiz state
let quizState = {
  currentQuestion: 0,
  answers: {},
  totalQuestions: 0
};

/**
 * Initialize the quiz functionality
 * 
 * @param {number} questionCount - Total number of questions in the quiz
 */
function initQuiz(questionCount) {
  quizState.totalQuestions = questionCount;
  
  // Show the first question
  showQuestion(0);
  
  // Set up event listeners
  document.querySelectorAll('.quiz-navigation button').forEach(button => {
    button.addEventListener('click', handleNavigation);
  });
  
  // Set up option selection
  document.querySelectorAll('.option-input').forEach(input => {
    input.addEventListener('change', handleOptionSelect);
  });
}

/**
 * Show a specific question
 * 
 * @param {number} questionIndex - Index of the question to show
 */
function showQuestion(questionIndex) {
  // Hide all questions
  document.querySelectorAll('.question').forEach(question => {
    question.style.display = 'none';
  });
  
  // Show the selected question
  const questionElement = document.getElementById(`question-${questionIndex}`);
  if (questionElement) {
    questionElement.style.display = 'block';
  }
  
  // Update current question
  quizState.currentQuestion = questionIndex;
  
  // Update navigation buttons
  updateNavigation();
  
  // Restore any previously selected answer
  const savedAnswer = quizState.answers[questionIndex];
  if (savedAnswer !== undefined) {
    const radioBtn = document.querySelector(`input[name="question_${questionIndex}"][value="${savedAnswer}"]`);
    if (radioBtn) {
      radioBtn.checked = true;
    }
  }
}

/**
 * Handle quiz navigation (next/previous buttons)
 * 
 * @param {Event} event - Click event
 */
function handleNavigation(event) {
  const action = event.target.dataset.action;
  
  if (action === 'next') {
    // Only proceed if an option is selected
    if (quizState.answers[quizState.currentQuestion] !== undefined) {
      if (quizState.currentQuestion < quizState.totalQuestions - 1) {
        showQuestion(quizState.currentQuestion + 1);
      } else {
        submitQuiz();
      }
    } else {
      // Show error message
      showMessage('Please select an answer before proceeding', 'error');
    }
  } else if (action === 'prev') {
    if (quizState.currentQuestion > 0) {
      showQuestion(quizState.currentQuestion - 1);
    }
  }
}

/**
 * Handle option selection
 * 
 * @param {Event} event - Change event
 */
function handleOptionSelect(event) {
  const questionId = parseInt(event.target.name.split('_')[1]);
  const answerId = parseInt(event.target.value);
  
  // Save the answer
  quizState.answers[questionId] = answerId;
  
  // Enable next button if disabled
  const nextButton = document.querySelector('[data-action="next"]');
  if (nextButton) {
    nextButton.disabled = false;
  }
}

/**
 * Update navigation buttons based on current question
 */
function updateNavigation() {
  const prevButton = document.querySelector('[data-action="prev"]');
  const nextButton = document.querySelector('[data-action="next"]');
  
  if (prevButton) {
    prevButton.disabled = quizState.currentQuestion === 0;
  }
  
  if (nextButton) {
    // Change button text for last question
    if (quizState.currentQuestion === quizState.totalQuestions - 1) {
      nextButton.textContent = 'Submit Quiz';
    } else {
      nextButton.textContent = 'Next';
    }
    
    // Disable if no answer selected
    nextButton.disabled = quizState.answers[quizState.currentQuestion] === undefined;
  }
}

/**
 * Submit the quiz
 */
function submitQuiz() {
  // Check if all questions are answered
  if (Object.keys(quizState.answers).length < quizState.totalQuestions) {
    showMessage('Please answer all questions before submitting', 'error');
    
    // Show the first unanswered question
    for (let i = 0; i < quizState.totalQuestions; i++) {
      if (quizState.answers[i] === undefined) {
        showQuestion(i);
        break;
      }
    }
    return;
  }
  
  // Click the hidden submit button
  document.getElementById('quiz-submit').click();
}

/**
 * Show a message to the user
 * 
 * @param {string} message - Message text
 * @param {string} type - Message type (error, success, info)
 */
function showMessage(message, type) {
  const messageElement = document.createElement('div');
  messageElement.className = `alert alert-${type}`;
  messageElement.textContent = message;
  
  const quizContainer = document.querySelector('.quiz-container');
  quizContainer.insertBefore(messageElement, quizContainer.firstChild);
  
  // Remove message after 5 seconds
  setTimeout(() => {
    messageElement.remove();
  }, 5000);
}
