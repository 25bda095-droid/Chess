# Project Changelog

## [2026-07-07] - Bonus Enhancements
- **Added:** `engine/search/mcts.py` implementing Monte Carlo Tree Search using AlphaZero principles.
- **Added:** `engine/search/tablebase.py` for exact Syzygy endgame tablebase querying.
- **Added:** `personalization/puzzle_rush.py` allowing users to solve auto-generated puzzles from their blunder history.
- **Added:** `explanation/tts_commentary.py` integrating multi-lingual TTS with Hindi commentary prompts.
- **Added:** `docs/verification_report.md` proving strict adherence to the project rules and constraints.
- **Added:** `docs/enhancements_report.md` documenting the details of the bonus extensions.

## [2026-07-07] - Phase 6 Product Surface & Polish
- **Added:** Scaffolding for React frontend using Vite in `frontend/` including `react-chessboard` and `chess.js` integration.
- **Added:** FastAPI backend in `backend/main.py` with endpoints `POST /api/move`, `GET /api/evaluation`, and `GET /api/explanation`.
- **Added:** `docs/phase6_report.md` summarizing frontend and backend implementation.

## [2026-07-07] - Phase 5 Streaming Personalization Engine
- **Added:** `personalization/mistake_tracker.py` containing `MistakeTracker` to log user mistake categories and maintain a vulnerability profile.
- **Added:** `personalization/slider_controller.py` containing `SliderController` which dynamically auto-tunes engine difficulty and aggression sliders based on weighted user mistake data (blunders, mistakes, inaccuracies).
- **Added:** `docs/phase5_report.md` detailing the integration and functionalities of the Phase 5 modules.

## [2026-07-07] - Phase 1 Initial Scaffolding
- **Added:** Core directory structure established for engine, backend, frontend, docs, and analysis.
- **Added:** `engine/core/board.py` initialized with a `python-chess` wrapper for the board state and move generator.
- **Added:** `engine/uci/uci_shim.py` implemented to handle standard UCI commands (`isready`, `position`, `go`) via standard I/O.
- **Added:** `engine/nnue/network.py` scaffolded with PyTorch structure (`FeatureTransformer` and `NNUE` module).
- **Added:** Tracking files (`project_tracker.md`, `changelog.md`, `file_graph.md`) and `.agyrules` for continuous AI assistant synchronization.
- **Added:** Initial `.gitignore` to prevent PyTorch weights, virtual environments, and python cache from being pushed.

## [2026-07-07] - Phase 4 Analysis & Explanation Layer
- **Added:** `analysis/blunder_detection.py` for evaluating score drops and classifying move qualities.
- **Added:** `explanation/prompt_templates.py` containing LLM coaching prompts.
- **Added:** `explanation/grounding_validator.py` implementing the `GroundingValidator` to enforce PV data constraint on LLM responses.

## [2026-07-07] - Phase 2 NNUE Evaluation Network
- **Added:** `engine/nnue/features.py` implementing HalfKP encoding strategy.
- **Added:** `engine/nnue/train.py` with dummy dataloader and PyTorch training loop.
- **Added:** `engine/nnue/validate.py` to benchmark inference speed.

## [2026-07-07] - Phase 3 Search, Self-Play & RL Loop
- **Added:** `engine/search/alphabeta.py` implementing `AlphaBetaSearch` with iterative deepening.
- **Added:** `engine/search/__init__.py` to expose the search interface.
- **Added:** `engine/selfplay/loop.py` for generating (state, policy, value) tuples via engine self-play.
- **Added:** `engine/selfplay/policy_value_net.py` with an AlphaZero-style policy and value network.
- **Added:** `benchmarking/elo_tracker.py` for automating matches against Stockfish and computing Elo.
- **Added:** `docs/phase3_report.md` summarizing the completed Phase 3 work.
