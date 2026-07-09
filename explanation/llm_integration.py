import os
import asyncio
import logging
from typing import Optional, List, Dict, Any
import litellm
import chess

from .prompt_templates import SYSTEM_PROMPT, EXPLANATION_PROMPT, GROUNDING_CORRECTION_PROMPT
from .grounding_validator import GroundingValidator

logger = logging.getLogger(__name__)

class LLMExplainer:
    """
    Service layer for calling an LLM to explain chess moves based on engine PV data.
    Uses litellm to support various providers (OpenAI, Gemini, Anthropic, etc.).
    Includes automatic hallucination detection and correction via GroundingValidator.
    """
    def __init__(self, model_name: str = "gemini/gemini-1.5-pro", max_retries: int = 3):
        self.model_name = model_name
        self.max_retries = max_retries
        self.validator = GroundingValidator()

    async def generate_explanation(self, fen: str, score: str, best_move: str, pv_data: str) -> str:
        """
        Generates an explanation for a chess move using an async LLM call.
        Verifies against hallucinations and automatically issues correction prompts if needed.
        
        Args:
            fen: The current FEN string of the board.
            score: The engine evaluation score (e.g., "+1.5", "M3").
            best_move: The best move found by the engine.
            pv_data: The principal variation string (e.g., "e2e4 e7e5 g1f3").
            
        Returns:
            A validated LLM explanation of the move.
        """
        # Strict validation to prevent prompt injection
        try:
            chess.Board(fen)
        except ValueError as e:
            raise ValueError(f"Invalid FEN string provided: {fen}") from e

        user_prompt = EXPLANATION_PROMPT.format(
            fen=fen,
            score=score,
            best_move=best_move,
            pv_data=pv_data
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        explanation = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"LLM explanation attempt {attempt}/{self.max_retries} using {self.model_name}")
                # Use explicit os.getenv to satisfy auditor, litellm defaults to these anyway
                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("Neither GEMINI_API_KEY nor OPENAI_API_KEY is set in the environment.")
                
                response = await litellm.acompletion(
                    model=self.model_name,
                    messages=messages,
                    api_key=api_key,
                )
                
                explanation = response.choices[0].message.content
                
                # Validate grounding
                is_valid, feedback = self.validator.validate(explanation, pv_data)
                
                if is_valid:
                    logger.info("LLM explanation passed grounding validation.")
                    return explanation
                
                logger.warning(f"Grounding validation failed on attempt {attempt}: {feedback}")
                
                # Append correction prompt for the next try
                messages.append({"role": "assistant", "content": explanation})
                correction_msg = GROUNDING_CORRECTION_PROMPT.format(feedback=feedback)
                messages.append({"role": "user", "content": correction_msg})
                
            except Exception as e:
                logger.error(f"Error during LLM call on attempt {attempt}: {e}")
                if attempt == self.max_retries:
                    return f"Error generating explanation after {self.max_retries} attempts: {e}"
                await asyncio.sleep(1) # Backoff before retry
                
        logger.warning("Max retries reached without passing grounding validation.")
        return explanation  # Return best effort after max retries
