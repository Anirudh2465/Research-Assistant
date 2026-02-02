import json
from backend.services.llm_extraction import llm_extractor

class LLMReasoning:
    def check_contradiction(self, concept_a, concept_b):
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
            return llm_extractor._call_llm(messages) # Reusing raw call method or similar
            # Ideally parse JSON here
        except:
            return None

    def synthesize_ideas(self, concepts, mode):
        # Legacy/Simple wrapper (mapped to Mode 1 or general)
        return self.synthesize_idea_advanced(concepts, mode)

    def synthesize_idea_advanced(self, concepts, mode, project_constraints=None):
        concept_summ = [f"{c['properties'].get('name')}: {c['properties'].get('description')}" for c in concepts]
        
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
            "novelty_score": 0.0-1.0,
            "feasibility_score": 0.0-1.0
        }}
        """
        messages = [{"role": "user", "content": prompt}]
        try:
            return llm_extractor._call_llm(messages)
        except:
            return None

    def analyze_blockers(self, idea_context):
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
            return llm_extractor._call_llm(messages)
        except:
            return None

llm_reasoning = LLMReasoning()
