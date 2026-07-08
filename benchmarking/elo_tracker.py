import sys
import os
import math
from tqdm import tqdm
import chess

# 1. Setup sys.path to allow imports from engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Import required classes
from engine.selfplay.loop import NNUEMCTSAgent
from engine.core.board import Board

def main():
    base_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nnue_base_model_final.pth'))
    rl_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nnue_rl_model_final.pth'))

    print("Loading Base Agent...")
    # 3. Instantiate agents
    base_agent = NNUEMCTSAgent(model_path=base_model_path, simulations=25)
    
    print("Loading RL Agent...")
    rl_agent = NNUEMCTSAgent(model_path=rl_model_path, simulations=25)

    num_games = 20
    rl_points = 0.0

    print(f"\nStarting Arena Match: {num_games} Games")
    
    # 8. Print a beautiful summary of the match to the terminal using tqdm for the games
    # 4. Arena match of 20 games
    for game_idx in tqdm(range(num_games), desc="Arena Match"):
        board = Board()
        
        # In 10 games rl_agent is White, and in 10 games it's Black
        rl_is_white = (game_idx < 10)
        
        # 5. Game loop
        while not board.is_game_over():
            is_white_turn = (board._board.turn == chess.WHITE)
            
            if (is_white_turn and rl_is_white) or (not is_white_turn and not rl_is_white):
                current_agent = rl_agent
            else:
                current_agent = base_agent
                
            # Ask the appropriate agent for a move
            policy = current_agent.search_and_get_policy(board)
            move = current_agent.sample_move(policy, board)
            
            # Push it to the board
            board.push(move)
            
        result = board.get_result()
        
        # 6. Track RL agent's score: Win = 1, Draw = 0.5
        if result == "1-0":
            if rl_is_white:
                rl_points += 1.0
        elif result == "0-1":
            if not rl_is_white:
                rl_points += 1.0
        elif result == "1/2-1/2":
            rl_points += 0.5
            
    # 7. Calculate Elo difference
    expected_score = rl_points / num_games
    
    if expected_score == 1.0:
        elo_diff = float('inf')
    elif expected_score == 0.0:
        elo_diff = float('-inf')
    else:
        elo_diff = -400 * math.log10(1 / expected_score - 1)
        
    print("\n" + "="*40)
    print("🏆 Match Summary 🏆")
    print("="*40)
    print(f"Total Games: {num_games}")
    print(f"RL Agent Points: {rl_points} / {num_games}")
    print(f"Win Rate: {expected_score * 100:.1f}%")
    
    if expected_score == 1.0:
        print("Elo Gained by RL Model: +∞ (100% win rate)")
    elif expected_score == 0.0:
        print("Elo Gained by RL Model: -∞ (0% win rate)")
    else:
        print(f"Elo Gained by RL Model: {elo_diff:+.2f} Elo")
    print("="*40)

if __name__ == "__main__":
    main()
