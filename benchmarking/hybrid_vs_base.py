import chess
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.selfplay.loop import NNUEMCTSAgent
from engine.core.board import Board

def run_hybrid_arena():
    print("Loading Pure Base Agent (No RL, No Tablebases)...")
    base_agent = NNUEMCTSAgent(model_path="nnue_base_model_final.pth", simulations=20, use_tablebase=False)
    
    print("Loading Hybrid RL Agent (RL Trained + Lichess Tablebase Hook)...")
    hybrid_agent = NNUEMCTSAgent(model_path="nnue_rl_model_final.pth", simulations=20, use_tablebase=True)
    
    games_to_play = 5
    hybrid_score = 0.0
    
    print(f"\n--- Starting {games_to_play}-Game Blitz Match: Hybrid RL Agent vs Pure Base Agent ---")
    
    for i in range(games_to_play):
        board = Board()
        hybrid_is_white = (i % 2 == 0)
        print(f"\nGame {i+1}/{games_to_play}: Hybrid RL Agent is {'White' if hybrid_is_white else 'Black'}")
        
        while not board.is_game_over():
            if (board._board.turn == chess.WHITE and hybrid_is_white) or (board._board.turn == chess.BLACK and not hybrid_is_white):
                policy = hybrid_agent.search_and_get_policy(board)
                move = hybrid_agent.sample_move(policy, board)
            else:
                policy = base_agent.search_and_get_policy(board)
                move = base_agent.sample_move(policy, board)
                
            board.push(move)
            
        res = board.get_result()
        if res == "1-0":
            if hybrid_is_white: hybrid_score += 1.0; print("Result: Hybrid RL Agent WINS!")
            else: print("Result: Pure Base Agent WINS.")
        elif res == "0-1":
            if not hybrid_is_white: hybrid_score += 1.0; print("Result: Hybrid RL Agent WINS!")
            else: print("Result: Pure Base Agent WINS.")
        else:
            hybrid_score += 0.5
            print(f"Result: DRAW (Reason: {board.get_fen()})")
            
    print("\n--- FINAL RESULTS ---")
    print(f"Hybrid RL Agent Score: {hybrid_score} out of {games_to_play}")
    
    if hybrid_score > games_to_play / 2:
        print("VERDICT: The Hybrid RL Agent successfully defeated the Base Model! The RL + Tablebase pipeline is officially a massive success.")
    elif hybrid_score == games_to_play / 2:
        print("VERDICT: Tie. The AIs are evenly matched.")
    else:
        print("VERDICT: Pure Base Agent won.")

if __name__ == "__main__":
    run_hybrid_arena()
