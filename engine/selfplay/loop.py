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
            A list of tuples: (state_fen, policy_dict, value_from_perspective) and the winner string.
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
            
        return data, result_str

    def generate_data(self, agent, num_games: int) -> List[Tuple[str, dict, float]]:
        from tqdm import tqdm
        dataset = []
        stats = {'White Wins': 0, 'Black Wins': 0, 'Draws': 0, 'Mistakes': 0}
        
        pbar = tqdm(range(num_games), desc="Self-Play RL")
        for i in pbar:
            game_data, result_str = self.play_single_game(agent)
            dataset.extend(game_data)
            
            if result_str == "1-0":
                stats['White Wins'] += 1
            elif result_str == "0-1":
                stats['Black Wins'] += 1
            else:
                stats['Draws'] += 1
                
            # Track mistakes (mock logic: arbitrary blunders during MCTS)
            stats['Mistakes'] += len(game_data) // 15
            
            pbar.set_postfix(stats)
            
        print("\n--- Self-Play RL Session Complete ---")
        for k, v in stats.items():
            print(f"{k}: {v}")
            
        return dataset

import torch
from engine.nnue.network import NNUE
from engine.nnue.features import HalfKPFeatures
from engine.search.mcts import AlphaZeroMCTS

class NNUEMCTSAgent:
    """Agent that uses our trained NNUE model and MCTS to play."""
    def __init__(self, model_path="nnue_base_model_final.pth", simulations=50):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = NNUE(input_size=HalfKPFeatures.NUM_FEATURES, embedding_size=32, hidden_size=16)
        
        if os.path.exists(model_path):
            print(f"Loading trained brain: {model_path}")
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        else:
            print(f"Warning: {model_path} not found. Using untrained brain.")
            
        self.model.to(self.device)
        self.model.eval()
        self.mcts = AlphaZeroMCTS(self.evaluate_board, num_simulations=simulations)

    def evaluate_board(self, board):
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return {}, 0.0
            
        # 1. Dummy Policy (equal chance for all moves) since we only trained a Value Network
        policy = {move: 1.0/len(legal_moves) for move in legal_moves}
        
        # 2. Real NNUE Value Evaluation
        sparse = HalfKPFeatures.board_to_tensor(board).to_dense()
        feat_stm = sparse[0].unsqueeze(0).to(self.device)
        feat_nstm = sparse[1].unsqueeze(0).to(self.device)
        
        if board.turn != chess.WHITE:
            feat_stm, feat_nstm = feat_nstm, feat_stm
            
        with torch.no_grad():
            val = self.model(feat_stm, feat_nstm).item()
            
        val = max(-1.0, min(1.0, val)) # Clamp to [-1, 1] for MCTS
        return policy, val

    def search_and_get_policy(self, board):
        # High temperature for the first 30 ply (15 moves) to force opening exploration!
        # After 30 ply, temperature drops to 0 so it plays perfectly deterministically.
        ply_count = len(board._board.move_stack)
        temp = 1.0 if ply_count < 30 else 0.0
        
        # MCTS now returns a dictionary of probabilities instead of a single move
        policy = self.mcts.search(board._board, temperature=temp)
        return {move.uci(): prob for move, prob in policy.items()}

    def sample_move(self, policy, board):
        import random
        moves = list(policy.keys())
        probs = list(policy.values())
        chosen_uci = random.choices(moves, weights=probs, k=1)[0]
        return chess.Move.from_uci(chosen_uci)

if __name__ == "__main__":
    # Test the self-play loop with our REAL trained agent
    loop = SelfPlayLoop()
    agent = NNUEMCTSAgent(model_path="nnue_base_model_final.pth", simulations=50)
    print("Starting a real self-play session with NNUE + MCTS...")
    data = loop.generate_data(agent, num_games=500)
    
    print(f"\nGenerated a massive dataset of {len(data)} RL positions!")
    print("Saving self-play data to disk for Phase 2 Reinforcement Learning...")
    torch.save(data, "rl_selfplay_data.pt")
    print("Successfully saved to 'rl_selfplay_data.pt'!")
