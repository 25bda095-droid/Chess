import math
import chess

class Node:
    """
    A node in the MCTS tree.
    """
    def __init__(self, state, parent=None, prior_prob=0.0):
        self.state = state
        self.parent = parent
        self.children = {}  # Action (chess.Move) -> Node
        self.visits = 0
        self.value_sum = 0.0
        self.prior_prob = prior_prob

    @property
    def q_value(self):
        """Returns the average value of the node."""
        if self.visits == 0:
            return 0.0
        return self.value_sum / self.visits

    def expand(self, action_probs):
        """
        Expands the node using the policy network's action probabilities.
        
        Args:
            action_probs: A dictionary of {chess.Move: probability} for all legal moves.
        """
        for move, prob in action_probs.items():
            if move not in self.children:
                next_state = self.state.copy()
                next_state.push(move)
                self.children[move] = Node(next_state, parent=self, prior_prob=prob)

    def is_expanded(self):
        """Returns True if the node has been expanded."""
        return len(self.children) > 0


class AlphaZeroMCTS:
    """
    Monte Carlo Tree Search implementation tailored for an AlphaZero-style 
    engine utilizing policy and value neural networks.
    """
    def __init__(self, policy_value_fn, c_puct=1.5, num_simulations=800):
        """
        Args:
            policy_value_fn: Function that takes a `chess.Board` state and returns:
                             - action_probs: dict of {chess.Move: prob}
                             - value: float in [-1, 1]
            c_puct: Constant determining exploration weight.
            num_simulations: Number of iterations to run per search.
        """
        self.policy_value_fn = policy_value_fn
        self.c_puct = c_puct
        self.num_simulations = num_simulations

    def search(self, initial_state):
        """
        Runs MCTS starting from the given state and returns the best move.
        
        Args:
            initial_state: The root `chess.Board` state.
            
        Returns:
            The best `chess.Move` based on highest visit count.
        """
        root = Node(initial_state)
        
        # Initial expansion of the root node
        action_probs, _ = self.policy_value_fn(initial_state)
        root.expand(action_probs)

        for _ in range(self.num_simulations):
            node = root
            
            # 1. Selection
            while node.is_expanded():
                best_score = -float('inf')
                best_child = None
                
                for action, child in node.children.items():
                    # PUCT Algorithm: Q(s, a) + c_puct * P(s, a) * sqrt(N(s)) / (1 + N(s, a))
                    u_value = self.c_puct * child.prior_prob * math.sqrt(node.visits) / (1 + child.visits)
                    score = child.q_value + u_value
                    
                    if score > best_score:
                        best_score = score
                        best_child = child
                        
                node = best_child

            # 2. Expansion and Evaluation
            if not node.state.is_game_over():
                action_probs, value = self.policy_value_fn(node.state)
                node.expand(action_probs)
            else:
                # Use terminal values directly instead of network evaluation
                result = node.state.result()
                if result == '1-0':
                    value = 1.0 if node.state.turn == chess.WHITE else -1.0
                elif result == '0-1':
                    value = -1.0 if node.state.turn == chess.WHITE else 1.0
                else:
                    value = 0.0  # Draw

            # 3. Backpropagation
            current = node
            # The network/terminal evaluation is w.r.t the player whose turn it is at `node.state`
            # For its parent, the value should be inverted.
            v = -value 
            
            while current.parent is not None:
                current.visits += 1
                current.value_sum += v
                current = current.parent
                v = -v  # Switch perspective for the other player
                
            root.visits += 1

        # Best move is the one most visited, per AlphaZero paper
        best_move = max(root.children.items(), key=lambda item: item[1].visits)[0]
        return best_move
