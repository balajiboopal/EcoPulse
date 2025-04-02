"""
Quiz Module

Provides educational quiz questions and scoring functionality for
teaching employees about sustainability and carbon footprint concepts.
"""

class SustainabilityQuiz:
    """
    A quiz system with sustainability-focused questions.
    
    Manages a database of questions, generates quizzes, and scores responses.
    """
    
    def __init__(self):
        """Initialize the quiz system with a question bank."""
        self.question_bank = self._create_question_bank()
    
    def _create_question_bank(self):
        """
        Create a bank of quiz questions about sustainability.
        
        Returns:
            list: Quiz questions with answers and explanations
        """
        return [
            {
                'id': 1,
                'category': 'General',
                'difficulty': 'easy',
                'question': 'Which of the following contributes most to greenhouse gas emissions globally?',
                'options': [
                    'Transportation',
                    'Electricity and heat production',
                    'Agriculture',
                    'Buildings'
                ],
                'correct_answer': 1,  # Electricity and heat production
                'explanation': 'Electricity and heat production account for approximately 25% of global greenhouse gas emissions, making it the largest contributor.'
            },
            {
                'id': 2,
                'category': 'Transportation',
                'difficulty': 'medium',
                'question': 'How much more carbon-efficient is taking a train compared to flying for the same journey?',
                'options': [
                    'About the same',
                    '2-3 times more efficient',
                    '5-10 times more efficient',
                    'Over 20 times more efficient'
                ],
                'correct_answer': 2,  # 5-10 times more efficient
                'explanation': 'Train travel is typically 5-10 times more carbon-efficient than flying for the same distance, making it one of the most sustainable long-distance travel options.'
            },
            {
                'id': 3,
                'category': 'Diet',
                'difficulty': 'easy',
                'question': 'Which food typically has the highest carbon footprint per pound?',
                'options': [
                    'Chicken',
                    'Beef',
                    'Rice',
                    'Vegetables'
                ],
                'correct_answer': 1,  # Beef
                'explanation': 'Beef has one of the highest carbon footprints of any food, requiring significant land, water, and feed while producing methane emissions.'
            },
            {
                'id': 4,
                'category': 'Office',
                'difficulty': 'easy',
                'question': 'What percentage of office waste is typically paper?',
                'options': [
                    'Less than 10%',
                    '20-30%',
                    '40-50%',
                    '70% or more'
                ],
                'correct_answer': 2,  # 40-50%
                'explanation': 'Paper typically makes up 40-50% of office waste, highlighting the importance of digital solutions and recycling programs.'
            },
            {
                'id': 5,
                'category': 'Energy',
                'difficulty': 'medium',
                'question': 'Which action saves the most energy in an office setting?',
                'options': [
                    'Turning off lights when not in use',
                    'Using energy-efficient light bulbs',
                    'Proper HVAC temperature settings',
                    'Using power strips for electronics'
                ],
                'correct_answer': 2,  # Proper HVAC temperature settings
                'explanation': 'HVAC systems account for about 40% of energy use in office buildings, making temperature management the most impactful energy-saving measure.'
            },
            {
                'id': 6,
                'category': 'General',
                'difficulty': 'hard',
                'question': 'What is the approximate global average carbon footprint per person per year?',
                'options': [
                    '1-2 metric tons CO₂',
                    '4-5 metric tons CO₂',
                    '7-8 metric tons CO₂',
                    'Over 10 metric tons CO₂'
                ],
                'correct_answer': 1,  # 4-5 metric tons CO₂
                'explanation': 'The global average carbon footprint is approximately 4-5 metric tons of CO₂ per person annually, though this varies significantly by country.'
            },
            {
                'id': 7,
                'category': 'Transportation',
                'difficulty': 'medium',
                'question': 'How much can carpooling with one additional person reduce your commute emissions?',
                'options': [
                    'By about 10%',
                    'By about 25%',
                    'By about 50%',
                    'By about 75%'
                ],
                'correct_answer': 2,  # By about 50%
                'explanation': 'Carpooling with one additional person cuts the per-person emissions roughly in half, making it one of the simplest ways to reduce commuting impact.'
            },
            {
                'id': 8,
                'category': 'Diet',
                'difficulty': 'hard',
                'question': 'Approximately how much water is required to produce 1 pound of beef?',
                'options': [
                    '100 gallons',
                    '500 gallons',
                    '1,800 gallons',
                    '5,000+ gallons'
                ],
                'correct_answer': 2,  # 1,800 gallons
                'explanation': 'It takes approximately 1,800 gallons of water to produce a single pound of beef, highlighting the significant water footprint of beef production.'
            },
            {
                'id': 9,
                'category': 'Office',
                'difficulty': 'medium',
                'question': 'What percentage of energy can be saved by setting computers to sleep mode when not in use?',
                'options': [
                    'Less than 10%',
                    '20-40%',
                    '60-80%',
                    'Over 90%'
                ],
                'correct_answer': 2,  # 60-80%
                'explanation': 'Setting computers to sleep mode can reduce their energy use by 60-80% compared to leaving them fully powered on but idle.'
            },
            {
                'id': 10,
                'category': 'Energy',
                'difficulty': 'easy',
                'question': 'Which of these light bulb types is most energy-efficient?',
                'options': [
                    'Incandescent',
                    'Halogen',
                    'Compact Fluorescent (CFL)',
                    'LED'
                ],
                'correct_answer': 3,  # LED
                'explanation': 'LED lights are the most energy-efficient option, using up to 80% less energy than incandescent bulbs and lasting much longer.'
            },
            {
                'id': 11,
                'category': 'General',
                'difficulty': 'medium',
                'question': 'What is the concept of "carbon neutrality"?',
                'options': [
                    'Producing zero carbon emissions',
                    'Balancing carbon emissions with carbon removal',
                    'Using only renewable energy',
                    'Reducing carbon emissions by 50%'
                ],
                'correct_answer': 1,  # Balancing carbon emissions with carbon removal
                'explanation': 'Carbon neutrality means achieving net-zero carbon emissions by balancing the amount of carbon released with an equivalent amount removed or offset.'
            },
            {
                'id': 12,
                'category': 'Transportation',
                'difficulty': 'hard',
                'question': 'What percentage of an average car\'s lifetime carbon footprint comes from its manufacturing?',
                'options': [
                    'Less than 5%',
                    '10-20%',
                    '20-30%',
                    '30-40%'
                ],
                'correct_answer': 2,  # 20-30%
                'explanation': 'About 20-30% of a conventional car\'s lifetime carbon footprint comes from its manufacturing process, with the remainder primarily from fuel consumption.'
            }
        ]
    
    def generate_quiz(self, num_questions=5, categories=None, difficulty=None):
        """
        Generate a quiz with specified parameters.
        
        Args:
            num_questions (int): Number of questions to include
            categories (list, optional): Filter by specific categories
            difficulty (str, optional): Filter by difficulty level
            
        Returns:
            list: Selected quiz questions
        """
        # Filter questions based on criteria
        filtered_questions = self.question_bank.copy()
        
        if categories:
            filtered_questions = [q for q in filtered_questions if q['category'] in categories]
            
        if difficulty:
            filtered_questions = [q for q in filtered_questions if q['difficulty'] == difficulty]
            
        # Ensure we have enough questions
        if len(filtered_questions) < num_questions:
            # Fall back to all questions if filters are too restrictive
            filtered_questions = self.question_bank.copy()
            
        # Select random subset up to num_questions
        import random
        if len(filtered_questions) > num_questions:
            quiz_questions = random.sample(filtered_questions, num_questions)
        else:
            quiz_questions = filtered_questions
            
        # For API/route consumption, include all question data
        # This will be used by the backend to score the quiz
        return quiz_questions
    
    def score_quiz(self, user_answers):
        """
        Score a completed quiz.
        
        Args:
            user_answers (list): List of {question_id, selected_answer} dictionaries
            
        Returns:
            dict: Quiz results with score, feedback, and explanations
        """
        # Map questions by ID for easy lookup
        questions_by_id = {q['id']: q for q in self.question_bank}
        
        # Calculate score
        correct_count = 0
        total_questions = len(user_answers)
        
        # Prepare detailed feedback
        results = []
        
        for answer in user_answers:
            question_id = answer.get('question_id')
            selected_answer = answer.get('selected_answer')
            
            # Skip if question not found
            if question_id not in questions_by_id:
                continue
                
            question = questions_by_id[question_id]
            correct = selected_answer == question['correct_answer']
            
            if correct:
                correct_count += 1
                
            # Add result details
            results.append({
                'question_id': question_id,
                'question_text': question['question'],
                'correct': correct,
                'selected_answer': selected_answer,
                'correct_answer': question['correct_answer'],
                'explanation': question['explanation'],
                'correct_text': question['options'][question['correct_answer']]
            })
            
        # Calculate percentage score
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        return {
            'score': correct_count,
            'total': total_questions,
            'percentage': round(percentage, 1),
            'results': results
        }
