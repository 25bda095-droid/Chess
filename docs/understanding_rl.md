# Understanding the Core Engine & Reinforcement Learning (RL)

This document explains the heart of this chess project: how the Artificial Intelligence works, how it learns, and what Reinforcement Learning actually is.

## 1. The Neural Network (NNUE)
Traditional chess engines (like old Stockfish) relied on humans writing thousands of lines of code to evaluate a board (e.g., "A Knight is worth 3 points", "A Pawn in the center is worth +0.5 points"). 

We used **NNUE (Efficiently Updatable Neural Network)**. Instead of human rules, the AI looks at a chess board as an array of 41,024 inputs (called `HalfKP` features—representing where every piece is relative to the Kings). 
It passes these inputs through a Neural Network (in `network.py`), which simply outputs a single number: **The Value**.
- `1.0` means White is completely winning.
- `-1.0` means Black is completely winning.
- `0.0` means it is a dead draw.

## 2. Phase 1: Base Model Training (Supervised Learning)
If you start a Neural Network from scratch, its weights are randomized. It thinks giving away its Queen is a brilliant idea.
To give it a "bootstrap" of knowledge, we performed **Supervised Learning** using `train.py`.
- We fed it 200,000 games played by human Grandmasters (the Lichess Elite `.pgn`).
- The AI looked at the board, made a random guess, and then we mathematically punished/rewarded it based on who *actually* won that human game.
- After 1 hour on your RTX 4050, it learned the fundamental rules of chess: piece values, King safety, and standard openings (like the Reti `g1f3`).

## 3. The Problem with Human Data (The Human Ceiling)
Supervised learning is great, but it has a fatal flaw: **The AI can only become as good as the humans it is copying.** Humans make mistakes. Humans miss 20-move checkmate combinations. If we only train on human data, the AI hits a "Human Ceiling" and can never surpass us.

## 4. Phase 2: Reinforcement Learning (Self-Play)
To break past the human limit, we introduced **Reinforcement Learning (RL)** via `loop.py`. 
This is the exact same philosophy Google DeepMind used for AlphaZero.

Instead of reading human games, the AI generates its *own* games by playing against itself millions of times. 
- **The Engine (MCTS):** It uses Monte Carlo Tree Search (`mcts.py`) to look 50 moves into the future. 
- **Imagination (Temperature):** For the first 15 moves, we inject mathematical randomness (`temperature=1.0`). This forces the AI to explore weird, unknown openings instead of just repeating the same game forever.
- **The Feedback Loop:** After the game finishes, it looks at the final result (Win/Loss/Draw). It then feeds that game *back* into its own brain, saying: *"Adjust your neural weights to favor the moves the winning side made."*

Through RL, the AI slowly deletes its human biases and discovers objective, mathematical truths about the chessboard that humans have never even seen before.

## 5. Summary of Core Files
- `engine/nnue/network.py`: The architecture of the AI brain.
- `engine/nnue/features.py`: Converts the chessboard into the 41,024 numbers the AI can read.
- `engine/nnue/train.py`: Teaches the AI by copying human Grandmasters.
- `engine/search/mcts.py`: The algorithm that looks into the future to pick the best move.
- `engine/selfplay/loop.py`: The RL arena where the AI fights itself to generate superhuman data.
