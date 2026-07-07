class SliderController:
    def __init__(self, initial_difficulty=50, initial_aggression=50):
        self.difficulty = initial_difficulty
        self.aggression = initial_aggression

    def tune_sliders(self, mistake_data):
        """
        Tunes the difficulty and aggression sliders based on user mistake data.
        
        Args:
            mistake_data (dict): A dictionary containing mistake counts, e.g.,
                                 {'blunders': 2, 'mistakes': 3, 'inaccuracies': 5, 'moves': 40}
        
        Returns:
            tuple: (new_difficulty, new_aggression) both in range [0, 100]
        """
        if not mistake_data or 'moves' not in mistake_data or mistake_data['moves'] == 0:
            return self.difficulty, self.aggression

        moves = mistake_data['moves']
        blunders = mistake_data.get('blunders', 0)
        mistakes = mistake_data.get('mistakes', 0)
        inaccuracies = mistake_data.get('inaccuracies', 0)

        # Calculate a weighted error score per move
        # Weights: blunder = 3, mistake = 2, inaccuracy = 1
        error_score = (blunders * 3 + mistakes * 2 + inaccuracies * 1) / moves

        # Base threshold for expected error score per move
        # If error_score > 0.15, user is struggling -> decrease difficulty
        # If error_score < 0.05, user is doing well -> increase difficulty
        
        if error_score > 0.15:
            # Decrease difficulty and aggression
            self.difficulty = max(0, self.difficulty - 10)
            self.aggression = max(0, self.aggression - 5)
        elif error_score < 0.05:
            # Increase difficulty and aggression
            self.difficulty = min(100, self.difficulty + 5)
            self.aggression = min(100, self.aggression + 5)

        return self.difficulty, self.aggression
