# Phase 4 Report: Analysis & Explanation Layer

## Overview
Phase 4 focused on translating raw chess engine evaluation data into human-readable analysis and explanations. This involved detecting critical moments in the game and strictly grounding a Large Language Model (LLM) to act as a chess coach without hallucinating lines.

## Components Implemented

### 1. Blunder and Inaccuracy Detection (`analysis/blunder_detection.py`)
- **Implemented By:** Analyzer Subagent
- **Description:** A `BlunderDetector` class was created to calculate evaluation score drops between consecutive moves.
- **Classification Thresholds:**
  - **Blunder:** Drop >= 300 centipawns
  - **Mistake:** Drop >= 100 centipawns
  - **Inaccuracy:** Drop >= 50 centipawns
  - **Normal:** Drop < 50 centipawns
- **Capabilities:** Correctly accounts for both White and Black turns.

### 2. Explanation Prompt Templates (`explanation/prompt_templates.py`)
- **Implemented By:** LLM Integrator Subagent
- **Description:** Contains templates to instruct the LLM:
  - `SYSTEM_PROMPT`: Instructs the LLM to act strictly as a chess coach explaining moves based *only* on provided Engine PV (Principal Variation) data.
  - `EXPLANATION_PROMPT`: Formats the inputs (FEN, engine evaluation, best move, Engine PV data) for the LLM.
  - `GROUNDING_CORRECTION_PROMPT`: Prompts the LLM for a revised explanation if validation fails.

### 3. Grounding Validator (`explanation/grounding_validator.py`)
- **Implemented By:** LLM Integrator Subagent
- **Description:** Contains the `GroundingValidator` class, responsible for preventing LLM hallucinations.
- **Capabilities:** Uses regex to extract standard chess moves (SAN and UCI) from the LLM's generated text and compares them against the Engine PV data. Un-grounded moves trigger a validation failure and feedback message for correction.
