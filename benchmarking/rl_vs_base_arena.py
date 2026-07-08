import chess
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.selfplay.loop import NNUEMCTSAgent
from engine.core.board import Board

def run_arena():
    print("Loading Phase 1 Base Brain...")
    base_agent = NNUEMCTSAgent(model_path="nnue_base_model_final.pth", simulations=20)
    
    print("Loading Phase 2 RL Brain...")
    rl_agent = NNUEMCTSAgent(model_path="nnue_rl_model_final.pth", simulations=20)
    
    games_to_play = 5
    rl_score = 0.0
    
    print(f"\n--- Starting {games_to_play}-Game Blitz Match: RL Agent vs Base Agent ---")
    
    for i in range(games_to_play):
        board = Board()
        rl_is_white = (i % 2 == 0)
        print(f"\nGame {i+1}/{games_to_play}: RL Agent is {'White' if rl_is_white else 'Black'}")
        
        while not board.is_game_over():
            if (board._board.turn == chess.WHITE and rl_is_white) or (board._board.turn == chess.BLACK and not rl_is_white):
                policy = rl_agent.search_and_get_policy(board)
                move = rl_agent.sample_move(policy, board)
            else:
                policy = base_agent.search_and_get_policy(board)
                move = base_agent.sample_move(policy, board)
                
            board.push(move)
            
        res = board.get_result()
        if res == "1-0":
            if rl_is_white: rl_score += 1.0; print("Result: RL Agent WINS!")
            else: print("Result: Base Agent WINS.")
        elif res == "0-1":
            if not rl_is_white: rl_score += 1.0; print("Result: RL Agent WINS!")
            else: print("Result: Base Agent WINS.")
        else:
            rl_score += 0.5
            print(f"Result: DRAW (Reason: {board.get_fen()})")
            
    print("\n--- FINAL RESULTS ---")
    print(f"RL Agent Score: {rl_score} out of {games_to_play}")
    
    if rl_score > games_to_play / 2:
        print("VERDICT: The Phase 2 RL Model crushed the Phase 1 Base Model! Your training is officially a success.")
    elif rl_score == games_to_play / 2:
        print("VERDICT: Tie. The RL Agent and Base Agent are equally matched.")
    else:
        print("VERDICT: Base Agent won. The RL training needs to run on more than 500 games to overcome the baseline.")

if __name__ == "__main__":
    run_arena()
