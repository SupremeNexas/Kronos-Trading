import os
import json
import logging
import requests
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class KronosLLMAgent:
    """
    LLM Agent for Kronos Agent Engine.
    Synthesizes numerical forecasts, market metrics, and past lessons into a rational decision.
    """

    def __init__(self, ollama_url: str = "http://localhost:11434/api/generate", model_name: str = "llama3.2:3b"):
        self.ollama_url = ollama_url
        self.model_name = model_name

    def analyze(
        self,
        symbol: str,
        current_price: float,
        kronos_prediction: Dict[str, Any],
        past_reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Runs LLM sentiment/technical analysis or rule-behavior replication.
        """
        # Formulate a structured prompt for the LLM
        prompt = self._build_prompt(symbol, current_price, kronos_prediction, past_reflections)

        # Try to contact local Ollama instance
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "think": False
                    }
                },
                timeout=10
            )
            if response.status_code == 200:
                text_response = response.json().get("response", "").strip()
                parsed = self._extract_json_response(text_response)
                if parsed:
                    return parsed
        except Exception as e:
            logger.warning(f"Ollama agent analysis request failed: {e}. Falling back to rule-based agent logic.")

        # Robust deterministic fallback if Ollama key/instance is unavailable
        return self._rule_based_analysis(symbol, current_price, kronos_prediction, past_reflections)

    def _build_prompt(
        self,
        symbol: str,
        current_price: float,
        kronos_prediction: Dict[str, Any],
        past_reflections: List[Dict[str, Any]]
    ) -> str:
        # Build prompt string
        reflections_str = ""
        for i, ref in enumerate(past_reflections):
            reflections_str += f"- Trade {i+1}: Action={ref.get('decision')}, Outcome={ref.get('outcome')}, Rtn={ref.get('return_pct')}%, Lesson={ref.get('lessons')}\n"

        if not reflections_str:
            reflections_str = "No past trades recorded for reference.\n"

        prompt = (
            f"You are the Kronos Lead Trading Agent. Review this trading opportunity:\n"
            f"Asset Symbol: {symbol}\n"
            f"Current Price: {current_price}\n"
            f"Kronos Prediction Details:\n"
            f"  - Forecasted Return: {kronos_prediction.get('return_pct', 0.0)}%\n"
            f"  - Forecasted Direction: {kronos_prediction.get('signal', 'HOLD')}\n"
            f"  - Estimated Support: {kronos_prediction.get('support', current_price * 0.95)}\n"
            f"  - Estimated Resistance: {kronos_prediction.get('resistance', current_price * 1.05)}\n\n"
            f"Past Trade Reflections & Lessons:\n{reflections_str}\n"
            f"Analyze current state and formulate a decision. You MUST return ONLY a JSON block in this exact schema, with no leading or trailing text:\n"
            f"{{\n"
            f"  \"action\": \"BUY\" | \"SELL\" | \"HOLD\",\n"
            f"  \"confidence\": <float between 0.0 and 1.0>,\n"
            f"  \"stop_loss\": <float proposed SL price>,\n"
            f"  \"take_profit\": <float proposed TP price>,\n"
            f"  \"reasoning\": \"<short sentence justification>\"\n"
            f"}}\n"
        )
        return prompt

    def _extract_json_response(self, text: str) -> Dict[str, Any]:
        try:
            # Simple extraction from markdown codes block if any
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text.strip())
            # Basic validation
            action = data.get("action", "HOLD").upper()
            if action not in ["BUY", "SELL", "HOLD"]:
                data["action"] = "HOLD"
            data["confidence"] = max(0.0, min(1.0, float(data.get("confidence", 0.5))))
            data["stop_loss"] = float(data.get("stop_loss", 0.0))
            data["take_profit"] = float(data.get("take_profit", 0.0))
            return data
        except Exception as e:
            logger.error(f"Failed to parse LLM json output: {e}. Output was: {text}")
            return None

    def _rule_based_analysis(
        self,
        symbol: str,
        current_price: float,
        kronos_prediction: Dict[str, Any],
        past_reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fallback implementation that implements high-quality analytical decision making.
        Avoids dependency on active local Ollama service.
        """
        signal = kronos_prediction.get("signal", "HOLD").upper()
        return_pct = kronos_prediction.get("return_pct", 0.0)
        support = kronos_prediction.get("support", current_price * 0.95)
        resistance = kronos_prediction.get("resistance", current_price * 1.05)

        # Review past failures to self-correct
        recent_failures_count = 0
        for ref in past_reflections:
            if ref.get("outcome") == "LOSS":
                recent_failures_count += 1

        # Calculate self-corrective confidence scaling
        confidence_multiplier = 1.0 - (0.15 * recent_failures_count)
        confidence_multiplier = max(0.4, confidence_multiplier)

        # Decide Action
        proposal_action = "HOLD"
        reason = "System forecasts sideways or low confidence trend."

        if signal == "BUY" and return_pct > 1.5:
            # Check if last buy trade failed
            if len(past_reflections) > 0 and past_reflections[0].get("decision") == "BUY" and past_reflections[0].get("outcome") == "LOSS":
                reason = "Avoiding consecutive BUY losses based on recent historical reflection."
                proposal_action = "HOLD"
            else:
                proposal_action = "BUY"
                reason = f"Bullish signal with +{return_pct}% return target."
        elif signal == "SELL" or return_pct < -1.5:
            # Check if last sell trade failed
            if len(past_reflections) > 0 and past_reflections[0].get("decision") == "SELL" and past_reflections[0].get("outcome") == "LOSS":
                reason = "Avoiding consecutive SELL losses based on recent historical reflection."
                proposal_action = "HOLD"
            else:
                proposal_action = "SELL"
                reason = f"Bearish signal with {return_pct}% forecast drop."

        # Compute SL/TP based on support/resistance
        if proposal_action == "BUY":
            # For buy: stop loss set exactly below support with a tiny buffer
            sl = min(support, current_price * 0.97)
            # Take profit set near resistance
            tp = max(resistance, current_price * 1.04)
            confidence = 0.85 * confidence_multiplier
        elif proposal_action == "SELL":
            sl = max(resistance, current_price * 1.03)
            tp = min(support, current_price * 0.96)
            confidence = 0.80 * confidence_multiplier
        else:
            sl = current_price * 0.95
            tp = current_price * 1.05
            confidence = 0.5 * confidence_multiplier

        return {
            "action": proposal_action,
            "confidence": float(round(confidence, 2)),
            "stop_loss": float(round(sl, 2)),
            "take_profit": float(round(tp, 2)),
            "reasoning": reason
        }
