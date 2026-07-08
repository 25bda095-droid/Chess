# File Graph and Architecture Links

This document links the core files of the project and describes their relationships.

## Core Directories & Files

### Engine (Core Chess Logic)
- `engine/core/board.py`: Manages the board state and legal move generation. Currently wraps `python-chess`.
- `engine/uci/uci_shim.py`: Interfaces with external chess GUIs via Standard Input/Output. Depends on `engine/core/board.py` to play moves.
- `engine/nnue/network.py`: PyTorch neural network for evaluating chess positions. 
- `engine/nnue/features.py`: Feature extraction logic (HalfKP encoding).
- `engine/nnue/train.py`: Supervised learning training loop and data loading.
- `engine/nnue/validate.py`: Validation script for model inference speed.
- `engine/search/`:
  - `__init__.py`: Exposes the search interface.
  - `alphabeta.py`: Implements AlphaBetaSearch with iterative deepening and alpha-beta pruning.
  - `mcts.py`: Monte Carlo Tree Search integrating policy and value network probabilities.
  - `tablebase.py`: Hooks into Syzygy tablebases for exact endgame evaluation.
- `engine/selfplay/`:
  - `loop.py`: Contains the self-play loop for RL training data generation.
  - `policy_value_net.py`: Contains the AlphaZero-style policy and value network.

### Subsystems
- `benchmarking/`:
  - `elo_tracker.py`: Script to run automated matches against a baseline engine and calculate Elo difference.
- `analysis/`:
  - `blunder_detection.py`: Calculates evaluation score drops to classify Blunders, Mistakes, and Inaccuracies.
- `explanation/`:
  - `prompt_templates.py`: LLM system and user prompts to explain moves based strictly on engine PV data.
  - `grounding_validator.py`: Regex-based validator to ensure LLM generated moves exist in PV data.
  - `tts_commentary.py`: Provides TTS capability and a custom Hindi commentary prompt template.
- `personalization/`: Contains user personalization logic.
  - `mistake_tracker.py`: Tracks user mistakes and identifies recurring vulnerabilities.
  - `slider_controller.py`: Auto-tunes interaction sliders (difficulty and aggression) based on user error scores.
  - `puzzle_rush.py`: Auto-generates puzzles based on the user's blunder history recorded in `mistake_tracker.py`.

### Product Interface
- `backend/`:
  - `main.py`: FastAPI backend defining endpoints for move submission, evaluation, and explanation.
- `frontend/`: React frontend scaffolded with Vite.
  - `src/App.jsx`: Main UI component rendering the `react-chessboard`.
  - `src/components/Dashboard.jsx`: Analytics visualization for user performance.

### Documentation & Tracking
- `docs/project_tracker.md`: High-level checklist of project phases and current status.
- `docs/changelog.md`: Summary of completed work by date.
- `docs/file_graph.md`: This file. Shows the architecture layout.
  - `docs/phase3_report.md`: Report detailing the Phase 3 search, self-play, and benchmarking implementation.
  - `docs/phase5_report.md`: Report detailing the Phase 5 streaming personalization implementation.
  - `docs/phase6_report.md`: Report detailing the Phase 6 product surface and polish implementation.
  - `docs/verification_report.md`: Audit report confirming adherence to project constraints.
  - `docs/enhancements_report.md`: Summary report of the bonus team extensions (MCTS, Tablebases, TTS, Puzzle Rush).
- `.agyrules`: Custom rules to force the AI to read/update the `docs/` files automatically.
  - `project.md`: The original problem statement and extended build plan.
