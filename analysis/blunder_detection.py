class BlunderDetector:
    def __init__(self, blunder_threshold=300, mistake_threshold=100, inaccuracy_threshold=50):
        """
        Initialize the detector with threshold values in centipawns.
        """
        self.blunder_threshold = blunder_threshold
        self.mistake_threshold = mistake_threshold
        self.inaccuracy_threshold = inaccuracy_threshold

    def calculate_drop(self, prev_eval, curr_eval, is_white_move):
        """
        Calculate the evaluation drop.
        Evaluations are assumed to be in centipawns from White's perspective.
        A positive drop indicates a worsening of the position for the player who just moved.
        """
        if is_white_move:
            return prev_eval - curr_eval
        else:
            return curr_eval - prev_eval

    def classify_move(self, drop):
        """
        Classify the move based on the evaluation drop.
        """
        if drop >= self.blunder_threshold:
            return "Blunder"
        elif drop >= self.mistake_threshold:
            return "Mistake"
        elif drop >= self.inaccuracy_threshold:
            return "Inaccuracy"
        return "Normal"

    def analyze_game(self, move_evaluations):
        """
        Analyze a list of evaluations to flag blunders, mistakes, and inaccuracies.
        
        move_evaluations: list of dicts containing:
            - 'eval': int (centipawns from white's perspective)
            - 'is_white': bool (True if it was White's move, False if Black's)
            - 'move': str (optional, algebraic notation)
            
        Returns: list of dicts with classification and drop added.
        """
        results = []
        prev_eval = 0  # Assuming standard starting position is roughly 0.00

        for move_data in move_evaluations:
            curr_eval = move_data.get('eval', 0)
            is_white = move_data.get('is_white', True)
            move = move_data.get('move', '')

            drop = self.calculate_drop(prev_eval, curr_eval, is_white)
            classification = self.classify_move(drop)

            results.append({
                'move': move,
                'is_white': is_white,
                'eval': curr_eval,
                'drop': drop,
                'classification': classification
            })

            prev_eval = curr_eval

        return results
