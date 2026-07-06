import chess
import numpy as np
import random
from typing import List, Tuple, Any, Dict
import os
import sys

# Ensure engine path is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from engine.core.board import Board

class SelfPlayLoop:
    """
    Self-Play Reinforcement Learning Data Generation Loop.
    Generates (state, policy, value) tuples by pitting the engine against itself.
    """
    def __init__(self, agent_config: Dict[str, Any] = None):
        """
        Initializes the self-play loop.
        agent_config can contain MCTS hyperparameters, model checkpoints, etc.
        """
        self.agent_config = agent_config or {}

    def play_single_game(self, agent) -> List[Tuple[str, dict, float]]:
        """
        Plays a single game of the engine against itself.
        
        Args:
            agent: The search agent (e.g., MCTS) that provides policy and value.
                   Must implement `search_and_get_policy(board)` and `sample_move(policy, board)`.
        
        Returns:
            A list of tuples: (state_fen, policy_dict, value_from_perspective)
        """
        board = Board()
        game_history = []
        
        while not board.is_game_over():
            fen_state = board.get_fen()
            
            # Agent performs search (e.g., MCTS) and returns a policy (visit distribution)
            policy = agent.search_and_get_policy(board)
            
            # Record state from perspective of the current player
            current_player = chess.WHITE if board._board.turn == chess.WHITE else chess.BLACK
            game_history.append((fen_state, policy, current_player))
            
            # Select move based on policy
            move = agent.sample_move(policy, board)
            board.push(move)

        # Game over, determine the outcome
        result_str = board.get_result()
        
        if result_str == "1-0":
            winner = chess.WHITE
        elif result_str == "0-1":
            winner = chess.BLACK
        else:
            winner = None # Draw
            
        # Assign values to the states in history based on the final outcome
        # 1.0 for a win, -1.0 for a loss, 0.0 for a draw from the perspective of the player to move
        data = []
        for state, policy, player in game_history:
            if winner is None:
                value = 0.0
            elif winner == player:
                value = 1.0
            else:
                value = -1.0
                
            data.append((state, policy, value))
            
        return data

    def generate_data(self, agent, num_games: int) -> List[Tuple[str, dict, float]]:
        """
        Generates self-play data by playing multiple games.
        
        Args:
            agent: The search agent.
            num_games: Number of games to play.
            
        Returns:
            Aggregated list of (state, policy, value) tuples from all games.
        """
        dataset = []
        for i in range(num_games):
            print(f"Playing game {i+1}/{num_games}...")
            game_data = self.play_single_game(agent)
            dataset.extend(game_data)
        
        return dataset

class DummyAgent:
    """A dummy agent for testing the self-play loop without a full MCTS/NNUE implementation."""
    def search_and_get_policy(self, board: Board) -> dict:
        legal_moves = board.generate_legal_moves()
        if not legal_moves:
            return {}
        prob = 1.0 / len(legal_moves)
        return {move.uci(): prob for move in legal_moves}

    def sample_move(self, policy: dict, board: Board) -> chess.Move:
        moves = list(policy.keys())
        probs = list(policy.values())
        chosen_uci = random.choices(moves, weights=probs, k=1)[0]
        return chess.Move.from_uci(chosen_uci)

if __name__ == "__main__":
    # Test the self-play loop with a dummy agent
    loop = SelfPlayLoop()
    dummy_agent = DummyAgent()
    print("Starting a test self-play game...")
    data = loop.generate_data(dummy_agent, num_games=1)
    
    print(f"Generated {len(data)} tuples from the test game.")
    print("Sample tuple (state, policy, value):")
    state, policy, value = data[0]
    print(f"State (FEN): {state}")
    print(f"Policy (Move Probabilities): {policy}")
    print(f"Value: {value}")
