import json
from backend.services.llm_extraction import llm_extractor
from backend.core.logging import logger


def _parse_json_response(raw: str) -> dict | None:
    """Helper: robustly extract the first JSON object or array from an LLM response."""
    if not raw:
        return None
    if isinstance(raw, dict):
        return raw
    try:
        # Try direct parse first
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    try:
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start != -1 and end != 0:
            return json.loads(raw[start:end])
    except json.JSONDecodeError:
        pass
    logger.warning("_parse_json_response: could not extract JSON from LLM output")
    return None


class LLMReasoning:
    def check_contradiction(self, concept_a: dict, concept_b: dict) -> dict | None:
        """
        Fix #12: Previously returned raw string. Now returns parsed dict or None.
        """
        prompt = f"""
        Do these two concepts contradict each other?

        Concept A: {json.dumps(concept_a)}
        Concept B: {json.dumps(concept_b)}

        A contradiction exists if they:
        - Make opposing assumptions
        - Claim incompatible results
        - Fail under mutually exclusive conditions

        Return JSON: {{ "contradiction": true/false, "explanation": "..." }}
        """
        messages = [{"role": "user", "content": prompt}]
        try:
            raw = llm_extractor._call_llm(messages)
            return _parse_json_response(raw)
        except Exception as e:
            logger.error(f"check_contradiction LLM call failed: {e}")
            return None

    def synthesize_ideas(self, concepts: list, mode: str) -> dict | None:
        # Legacy/Simple wrapper
        return self.synthesize_idea_advanced(concepts, mode)

    def synthesize_idea_advanced(
        self,
        concepts: list,
        mode: str,
        project_constraints: str | None = None
    ) -> dict | None:
        """
        Fix #12: Previously returned raw LLM string. Now returns a parsed dict or None.
        """
        concept_summ = [
            f"{c['properties'].get('name')}: {c['properties'].get('description')}"
            for c in concepts
        ]

        prompt = f"""
        Synthesize a Research Idea using Mode: {mode}.

        Input Concepts: {json.dumps(concept_summ)}
        Project Constraints: {project_constraints or 'None'}

        Modes:
        - Cross-Domain Transfer: Apply mechanism of A in domain of B.
        - Assumption Violation: Remove assumption X from A.
        - Limitation Bridging: Use B to address failure of A.
        - Scale Shift: Change resolution/dimensionality/temporal scale.
        - Method Stacking: Propose pipeline combining methods.

        Return JSON:
        {{
            "title": "...",
            "summary": "...",
            "novelty_explanation": "...",
            "expected_challenges": ["data", "theory", "compute"],
            "novelty_score": 0.0,
            "feasibility_score": 0.0
        }}
        """
        messages = [{"role": "user", "content": prompt}]
        try:
            raw = llm_extractor._call_llm(messages)
            return _parse_json_response(raw)
        except Exception as e:
            logger.error(f"synthesize_idea_advanced LLM call failed: {e}")
            return None

    def analyze_blockers(self, idea_context: dict) -> dict | None:
        """
        Fix #12: Previously returned raw LLM string. Now returns a parsed dict or None.
        """
        prompt = f"""
        Analyze "Why hasn't this been done yet?" for the following idea:

        Idea: {json.dumps(idea_context)}

        Identify blockers in: Data, Theory, Compute, Optimization, Evaluation.

        Return JSON:
        {{
            "blockers": [
                {{"category": "Data", "reason": "..."}},
                {{"category": "Theory", "reason": "..."}}
            ],
            "recommendation": "Next step..."
        }}
        """
        messages = [{"role": "user", "content": prompt}]
        try:
            raw = llm_extractor._call_llm(messages)
            return _parse_json_response(raw)
        except Exception as e:
            logger.error(f"analyze_blockers LLM call failed: {e}")
            return None

llm_reasoning = LLMReasoning()
