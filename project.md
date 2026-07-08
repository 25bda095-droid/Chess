# RL-Based Personalized Chess Assistant — Full Project Spec & Build Plan

> Source: IITISoC Problem Statements — AI/ML Track, Science & Technology Council, IIT Indore
> Domain: AI / ML | Difficulty: Advanced | Suggested Team Size: 4–6 members (solo-adapted notes included)
>
> This file contains the **full original problem statement** (transcribed in detail from the PDF) followed by an **expanded engineering build plan**. Anything I've added beyond the original spec — architecture choices, extra features, tooling, sequencing — is tagged `🔧 [UPGRADE]` so you can tell spec vs. suggestion at a glance.

---

## 1. Background

Traditional chess engines excel at calculating absolute mathematical move sequences, but they are not designed to tutor human players intuitively. Standard analysis toolkits flag an inaccuracy or a blunder without explaining the underlying positional concept, missed strategic objectives, or actionable corrective guidance.

This project bridges reinforcement learning (RL) engine architectures and interactive educational application design. The goal is a **localized chess assistant** capable of advanced gameplay evaluation, natural-language strategic breakdowns, and personalized adaptive feedback tailored directly to an individual's evolving style.

---

## 2. Core Objective

Design and implement an interactive chess assistant powered by a **custom reinforcement learning engine**. Given user game data, the platform must:

1. **(a)** Model a comprehensive chess environment to evaluate full game lifecycles.
2. **(b)** Optimize neural policy and value parameters via self-play networks, aiming for Grandmaster-level strength.
3. **(c)** Convert complex positional evaluation metrics into plain-language strategic lessons.
4. **(d)** Deploy an incremental tracking framework that adapts engine behavior and study themes based on repeating tactical vulnerabilities.

---

## 3. Scope of Work (Original Spec)

### 3.1 Chess Environment and NNUE Engine Design

- Establish a secure state handler to coordinate baseline moves, rules, and network evaluations.
- Implement an accurate move verification loop accounting for checks, promotions, castling, en passant, and draw conditions.
- Categorize discrete game states across opening, middlegame, and endgame intervals.
- Structure the engine evaluation framework using a **Neural Network Efficiently Updatable (NNUE)** architecture instead of raw static material scoring.
- Secure complete **Universal Chess Interface (UCI)** protocol compliance for the final engine executable.

### 3.2 Reinforcement Learning Engine Optimization

- Formulate self-play or engine-guided RL training iterations — explore policy gradients, actor-critic frameworks, PPO, or AlphaZero-style optimization structures.
- Drive long-term positional planning and calculation limits up to Grandmaster-level benchmarks.
- Track tactical strength improvements across all operational phases using systematic bot matches, with **Elo evaluated against Stockfish under uniform 30s+1s time controls**.

### 3.3 Game Evaluation & Analysis Tracking

- Build game evaluation/analysis tooling to monitor systemic model choices and compute gameplay correctness across a unified dashboard.
- Detect tactical blunders, positional trade calculations, and structural inaccuracies.
- Map relative aggression levels, defensive resourcefulness, and endgame conversion rates across distinct computational configurations for better accuracy.

### 3.4 Natural Language Explanation Layer

- Transform numeric evaluation data into accessible strategic commentary via language model text synthesis.
- Convert variations in engine score paths into human-readable tactical retrospectives.
- Deconstruct why an original move compromised safety or structure, and outline better alternative plans.
- Verify that textual output remains strictly grounded in engine data matrices to eliminate chess reasoning hallucinations.

### 3.5 Streaming Personalization Engine

- Implement active tracking vectors to log, analyze, and correct user vulnerabilities across historical sessions.
- Maintain a persistent storage profile mapping player game records and categorized mistakes.
- Utilize streaming or incremental machine learning loops to isolate repeated thematic flaws (e.g., poor king safety, hanging pieces, missed tactics, compromised pawn structures).
- Automatically adjust engine interaction sliders (difficulty, aggression, risk tolerance, positional vs. tactical bias) and recommend targeted study modules matched to user histories.

---

## 4. Technical Constraints (Original Spec — Hard Requirements)

| Constraint | Detail |
|---|---|
| **RL Integrity** | The final engine must actively use custom RL optimizations. **Wrapping an existing strong engine (Stockfish, Leela Chess Zero) as a pipeline is strictly prohibited.** |
| **Architectural Baseline** | Must implement an NNUE framework for core evaluation. Hard-coded static heuristic scoring is disallowed. |
| **API Restrictions** | LLMs are permitted *only* for narrative translation/explanation synthesis — never for core move generation or tactical decisions. |
| **Verification Metrics** | Elo performance must be validated programmatically via automated match scripts vs. Stockfish at explicit 30s+1s time controls. |
| **Compute Boundaries** | Must run efficiently on consumer hardware, using open-source ML/framework toolkits. |

---

## 5. Evaluation Criteria (Original Spec Weights)

| Dimension | Weight | Description |
|---|---|---|
| **Core Objectives** | 45% | RL optimization loop success, high-level play metrics, robust environment handling, precise LLM explanation layers, streaming personalization, interface completeness. |
| **Code Quality** | 20% | Clear decoupling of environment logic, policy network training, inference pipelines, explanation handlers, frontend state. |
| **Documentation** | 15% | Exhaustive setup guides, training configuration logs, reproducible baseline telemetry, robust Elo benchmarking logs. |
| **Product Ideation** | 10% | Practical utility for human learners, clarity of personalized feedback loops, responsiveness of sliders (aggression/difficulty). |
| **Presentation** | 10% | Walkthrough performance, validation via concrete chess examples, model comparisons, report professionalism. |

---

## 6. Bonus Extensions (Original Spec)

- **AlphaZero MCTS**: Integrate Monte Carlo Tree Search into the move selection pipeline.
- **Endgame Tablebase Hook**: Couple the engine with external endgame tablebases for perfect late-game evaluation.
- **Live Matchmaking Workspaces**: Real-time client interface for live gameplay against variable engine profiles.
- **Opening Repertoire Deep-Dives**: Diagnostic features mapping player opening trends against theoretical classification (ECO codes) to flag development risks.

---

## 7. Deliverables (Original Spec)

- **Codebase Repository** — clean, version-controlled, full engine files, training configs, explanation layers, setup instructions.
- **UCI Engine Executable** — functional, compiled binary using the optimized NNUE weights.
- **Product Workspace Interface** — web/API/desktop surface with adjustment sliders + PGN upload review.
- **Technical Benchmark Documentation** — network parameters, RL training methodology logs, inference speed profiles, evaluation charts, explanatory video.

---
---

# PART II — Expanded Engineering Build Plan

Everything below is my addition to help you actually execute this end-to-end. Tagged `🔧 [UPGRADE]` wherever it goes beyond the literal spec.

## 8. System Architecture 🔧 [UPGRADE]

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Web)                             │
│  React/Svelte board UI · sliders (difficulty/aggression/risk)     │
│  · PGN upload · live eval bar · routing dashboard · chat panel    │
└───────────────────────────┬─────────────────────────────────────┘
                             │ REST + WebSocket
┌───────────────────────────▼─────────────────────────────────────┐
│                     API / ORCHESTRATION LAYER                     │
│  FastAPI · session mgmt · auth · game store · UCI process pool    │
└───────┬───────────────┬───────────────┬───────────────┬─────────┘
        │               │               │               │
┌───────▼──────┐ ┌──────▼───────┐ ┌─────▼──────┐ ┌──────▼────────┐
│ Chess Engine │ │  Training    │ │ Explanation │ │ Personalization│
│ Core (C++/   │ │  Pipeline    │ │ Layer (LLM  │ │ Engine (mistake│
│ Rust or py-  │ │  (self-play, │ │ grounded on │ │ tracker, drift │
│ chess+NNUE)  │ │  PPO/AlphaZero│ │ engine data)│ │ detection)     │
│ UCI-compliant│ │  loop)       │ │             │ │                │
└──────────────┘ └──────────────┘ └─────────────┘ └────────────────┘
        │
┌───────▼───────────────────────────────────────────────────────────┐
│                          DATA LAYER                                 │
│  Postgres (users, games, mistake tags) · object storage for         │
│  checkpoints/NNUE weights · Redis for live session/eval cache       │
└──────────────────────────────────────────────────────────────────┘
```

## 9. Recommended Tech Stack 🔧 [UPGRADE]

Given your background (C++ for perf-critical code, Python/FastAPI comfort, free-tier deployment discipline from your other projects), here's a stack that keeps everything self-hostable at zero cost:

| Layer | Choice | Why |
|---|---|---|
| Engine core / move gen | **C++** with [python-chess](https://python-chess.readthedocs.io/) for prototyping, migrate hot path to C++ | Legal move gen + NNUE inference need speed; python-chess is great for fast iteration first |
| NNUE architecture | Custom small NNUE (à la Stockfish's, simplified) — feature transformer + 2 dense layers | Efficiently updatable, cheap CPU inference, satisfies the "no static heuristics" constraint |
| RL training | **PyTorch** + self-play loop (AlphaZero-style: policy+value net, MCTS-guided move selection) | Matches your existing PyTorch experience from other projects |
| Search | Custom alpha-beta w/ NNUE eval **or** MCTS guided by policy/value net (pick one as primary, other as bonus) | Alpha-beta+NNUE is lighter to reach usable strength fast; MCTS is the "AlphaZero" bonus path |
| UCI wrapper | Thin C++/Python UCI shim around your engine binary | Needed for constraint compliance + lets you benchmark vs Stockfish using any standard GUI (Arena, cutechess-cli) |
| Explanation LLM | Local small LLM (Ollama + a 7–8B instruct model) or a hosted API behind a strict "grounded-in-engine-data-only" prompt template | You've already built local LLM assistants (Jarvis) — reuse that pattern |
| Backend API | **FastAPI** (matches your Agentica/ShopMind stack) | You already know this stack cold |
| Frontend | React + a chess board lib (react-chessboard) + chart lib for eval graphs | Fast to build, matches your dashboard experience |
| DB | Postgres (Neon free tier — you've used this before) + Redis for live session state | Free-tier friendly, matches your accountability-bot infra |
| Deployment | Koyeb / Railway free tier for API, Vercel for frontend, engine training done locally/Colab | Consistent with your "zero-cost deployment" pattern across projects |
| Benchmarking | `cutechess-cli` for automated engine-vs-engine matches, Stockfish binary as the Elo yardstick | Standard tooling, satisfies "Verification Metrics" constraint |

## 10. Build Plan — 6 Phases 🔧 [UPGRADE]

No timeline attached — work through these at whatever pace fits. Each phase is scoped so you can validate it's actually working before moving to the next.

### Phase 1 — Core Engine Foundations
- Set up board representation (bitboards recommended for speed) + full legal move generator (checks, castling, en passant, promotion, threefold repetition, 50-move rule, stalemate).
- Write a perft (performance test) suite to validate move generation correctness against known perft values — this is the single most important correctness gate before anything else.
- Stand up the UCI protocol shim early so you can test against any standard GUI immediately.

### Phase 2 — NNUE Evaluation Network
- Design input feature set (e.g., HalfKP or a simplified king-relative piece-square encoding).
- Build the feature transformer (sparse-friendly) + small feed-forward stack.
- Bootstrap: train NNUE initially via supervised learning on a labeled dataset (e.g., positions labeled with Stockfish eval, **used only as training-data generation, not as a wrapped engine at inference** — this keeps you compliant with "no pipeline wrapper" since Stockfish is a *data labeler*, not your runtime engine).
  - 🔧 [UPGRADE] Document this distinction explicitly in your report — evaluators will care about this line.
- Validate inference speed (nodes/sec) — this determines your practical search depth.

### Phase 3 — Search, Self-Play RL Loop & Elo Benchmarking
- Implement alpha-beta with iterative deepening, transposition tables, move ordering (MVV-LVA, killer moves, history heuristic) as your baseline search — classical but necessary scaffolding.
- Layer in self-play RL: policy/value network + either (a) PPO over a simplified action space, or (b) AlphaZero-style MCTS guided by the policy/value net. Pick ONE as your primary path; document why.
- Set up a self-play data generation loop: play N games against past checkpoints, store (state, MCTS visit distribution, outcome) tuples, train, repeat — the standard AlphaZero training cycle.
- 🔧 [UPGRADE] Start with tiny board subsets or reduced time controls to get the training loop *working end-to-end* before scaling — validate the pipeline on short games before attempting anything resembling GM-level compute.
- Script automated matches vs. Stockfish (fixed, weaker skill levels initially, scaling up) using `cutechess-cli` at 30s+1s time control.
- Compute Elo via standard formula (or `bayeselo`/`ordo`) from match results, and log every checkpoint's Elo — this becomes your core "Core Objectives" evidence.

### Phase 4 — Analysis & Explanation Layer
- Blunder/inaccuracy detection: compare eval swing between consecutive moves against thresholds (e.g., >150cp drop = blunder, >75cp = mistake, >30cp = inaccuracy — tune to your NNUE's score scale).
- Phase classification (opening/middlegame/endgame) via piece-count + move-number heuristics.
- Aggregate stats: aggression score (captures/attacks initiated), defensive resourcefulness (successful threat parries), endgame conversion rate (win% from winning endgame positions).
- Design a strict prompt template for the explanation LLM that receives ONLY structured engine data (eval deltas, best-line PV, threatened pieces, positional features) — never let the LLM "guess" chess content.
- 🔧 [UPGRADE] Add a post-generation grounding check: regex/parse the LLM output for any move/square claims and cross-validate them against the actual engine PV before displaying — this directly satisfies "eliminate chess reasoning hallucinations" and is a strong differentiator in your report.
- Output format: "You played Nf3, but the engine's best line was e4 — this loses tempo because..." style retrospectives.

### Phase 5 — Streaming Personalization Engine
- Persistent per-user profile: mistake category counts over time (poor king safety, hanging pieces, missed tactics, weak pawn structure, time pressure blunders).
- Incremental update: each new game updates a running frequency table (simple exponential decay weighting works well and avoids needing a heavy streaming-ML framework).
- Auto-tune interaction sliders: e.g., if "hanging pieces" flagged in >30% of recent games, raise tactical-training weighting and lower engine playing difficulty temporarily to build confidence, then ramp back up.
- Study module recommender: map mistake categories → curated puzzle sets/openings to review (rule-based to start; 🔧 [UPGRADE] can later become a lightweight bandit/recommender model).

### Phase 6 — Product Surface, Documentation & Report
- Board UI with move input, live eval bar, PGN upload, slider panel (difficulty, aggression, risk tolerance, positional-vs-tactical bias).
- Personalization dashboard: mistake trend charts, Elo-over-time graph, phase-specific weak points.
- Post-game report view: full move list annotated with blunder/inaccuracy tags + LLM explanations inline.
- Technical report: architecture diagrams, NNUE design doc, RL training curves, Elo benchmark logs, ablations (e.g., alpha-beta+NNUE vs MCTS+policy-net comparison if you build both).
- Setup/reproduction guide + demo video: live gameplay, slider responsiveness, explanation quality, personalization loop over multiple simulated sessions.

## 11. Suggested Repository Structure 🔧 [UPGRADE]

```
chess-assistant/
├── engine/
│   ├── core/            # board repr, move gen, perft tests
│   ├── nnue/             # feature transformer, network, training scripts
│   ├── search/           # alpha-beta / MCTS
│   ├── uci/              # UCI protocol shim
│   └── selfplay/         # self-play data generation + RL training loop
├── benchmarking/
│   ├── cutechess_configs/
│   └── elo_tracker.py
├── analysis/
│   ├── blunder_detection.py
│   ├── phase_classifier.py
│   └── style_metrics.py
├── explanation/
│   ├── prompt_templates/
│   └── grounding_validator.py
├── personalization/
│   ├── mistake_tracker.py
│   └── slider_controller.py
├── backend/               # FastAPI app
├── frontend/              # React app
├── data/                  # training positions, PGN corpora
├── checkpoints/            # NNUE + policy/value weights (git-lfs or external storage)
├── reports/                # technical report, benchmark charts
└── docker-compose.yml
```

## 12. Data Sources 🔧 [UPGRADE]

- **Lichess open database** (free, monthly PGN dumps, millions of rated games) — use for supervised NNUE bootstrap labeling and opening statistics.
- **Lichess puzzle database** (free CSV) — great seed for your study-module recommender and for tactic-detection ground truth.
- Self-generated self-play games — your primary RL training data once the loop is stable.

## 13. Key Risks & Mitigations 🔧 [UPGRADE]

| Risk | Mitigation |
|---|---|
| Self-play RL from scratch to "GM-level" is compute-heavy (AlphaZero used TPU clusters) | Treat "Grandmaster-level" as an aspirational ceiling; report realistic Elo achieved on your compute budget and show the *trend line* — evaluators weight the training methodology heavily, not just raw Elo |
| NNUE training instability | Start with supervised bootstrap (Stockfish-labeled positions as ground truth for the *evaluation function only*) before layering RL fine-tuning on top |
| LLM hallucinating chess claims | Mandatory grounding validator (see Phase 4) — never skip this, it's an explicit constraint |
| Perft correctness bugs silently corrupting training | Perft test suite must pass before any training starts — this is non-negotiable |
| Scope creep across 8 subsystems | Build the UCI-compliant baseline engine (even if weak) end-to-end first — a working weak pipeline beats a strong but incomplete one for this rubric (45% weight is on "successful realization" across ALL subsystems) |

## 14. Stretch Goals Beyond the Official Bonus List 🔧 [UPGRADE]

- **Style cloning**: train a secondary small model to imitate the *user's* playing style (from their game history) so the assistant can suggest "moves you'd naturally consider" vs. "the objectively best move" — nice pedagogical contrast.
- **Voice explanation mode**: pipe the LLM explanation through TTS (you already have a Sarvam AI pipeline from Agentica/VOXAI) for spoken post-game reviews.
- **Puzzle rush mode**: auto-generate tactical puzzles from the user's own past blunders (turns their mistakes into personalized training material).
- **Hindi/Urdu commentary mode**: given your existing interest in Hindi audiobook generation, a Hindi-language explanation mode could be a distinctive differentiator for the "Product Ideation" score.

---

## 15. Immediate Next Actions

1. Set up board representation + move generator + perft validation (Phase 1).
2. Stand up the UCI shim so you can plug into a GUI/cutechess-cli immediately for sanity testing.
3. Decide primary search path: **alpha-beta+NNUE** (faster to reach playable strength) vs **MCTS+policy/value net** (closer to the AlphaZero bonus, heavier compute) — pick one as primary, keep the other as a documented bonus attempt.
4. Get the self-play data generation loop running end-to-end on a tiny scale before investing in longer training runs.
