"""Agent for generating concept examples on-demand.
Provides targeted examples when students request help with specific concepts.
"""

import logging
from typing import Optional
from pyd_models.schemas import ConceptExampleRequest, ConceptExampleResponse
from services import get_anthropic_client
from utils.json_parser import extract_json_from_response

logger = logging.getLogger(__name__)


class ConceptExampleAgent:
    """Agent responsible for generating on-demand concept examples"""
    
    def __init__(self):
        self.client = get_anthropic_client()
        self.max_retries = 3
    
    def generate_example(self, request: ConceptExampleRequest) -> ConceptExampleResponse:
        """
        Generate a concept example with retry logic.
        Categorizes the concept and provides appropriate example depth.
        """
        
        # First, categorize the concept
        example_type = self._categorize_concept(request.concept, request.known_language)
        
        # Generate the prompt
        prompt = self._get_example_prompt(
            concept=request.concept,
            language=request.programming_language,
            known_language=request.known_language,
            context=request.context,
            example_type=example_type
        )
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Concept Example Agent attempt {attempt + 1}/{self.max_retries} for concept: {request.concept}")
                response_text = self.client.generate_response(prompt, max_tokens=1000)
                
                data = extract_json_from_response(response_text)
                
                # Validate required fields
                requirements = ["code_example", "explanation"]
                for req in requirements:
                    if req not in data:
                        raise ValueError(f"Missing required field '{req}' in response data.")
                
                # Add fields that might be missing
                if "comparison_to_known" not in data:
                    data["comparison_to_known"] = None
                
                data["concept"] = request.concept
                data["example_type"] = example_type
                
                logger.info(f"Successfully generated example on attempt {attempt + 1}")
                return ConceptExampleResponse(**data)
                
            except (ValueError, KeyError) as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    prompt += f"\n\nIMPORTANT: Previous attempt failed. Ensure your response is ONLY valid JSON."
                continue
        
        logger.error(f"All {self.max_retries} attempts failed")
        raise ValueError(f"Failed to generate example after {self.max_retries} attempts: {str(last_error)}")
    
    def _categorize_concept(self, concept: str, known_language: Optional[str]) -> str:
        """
        Categorize the concept as basic, intermediate, or advanced.
        This determines the depth of the example.
        """
        concept_lower = concept.lower()
        
        # Basic concepts (1-3 line syntax templates)
        basic_concepts = [
            'loop', 'for loop', 'while loop', 'if', 'else', 'conditional',
            'variable', 'function', 'method', 'array', 'list', 'print',
            'input', 'string', 'integer', 'boolean', 'return'
        ]
        
        # Advanced concepts (10-15 line complete patterns)
        advanced_concepts = [
            'thread', 'async', 'await', 'delegate', 'event', 'linq',
            'lambda', 'closure', 'decorator', 'generator', 'coroutine',
            'mutex', 'semaphore', 'lock', 'concurrent', 'parallel',
            'generic', 'reflection', 'serialization', 'dependency injection'
        ]
        
        # Check if it's a basic concept
        for basic in basic_concepts:
            if basic in concept_lower:
                return "basic_syntax"
        
        # Check if it's an advanced concept
        for advanced in advanced_concepts:
            if advanced in concept_lower:
                return "advanced_pattern"
        
        # Everything else is intermediate
        return "intermediate_pattern"
    
    def _get_example_prompt(self, concept: str, language: str, 
                           known_language: Optional[str], context: Optional[str],
                           example_type: str) -> str:
        """Generate the prompt based on concept type and context"""
        
        # Determine example length based on type
        if example_type == "basic_syntax":
            length_instruction = "Provide a SHORT syntax template (1-3 lines) showing the basic structure."
            example_length = "1-3 lines"
        elif example_type == "intermediate_pattern":
            length_instruction = "Provide a working example (5-10 lines) demonstrating the concept in action."
            example_length = "5-10 lines"
        else:  # advanced_pattern
            length_instruction = "Provide a complete working pattern (10-15 lines) showing best practices and common usage."
            example_length = "10-15 lines"
        
        # Add known language comparison if provided
        comparison_section = ""
        if known_language:
            comparison_section = f"""
The student already knows {known_language}. In your explanation:
- If this concept has a direct equivalent in {known_language}, briefly mention it
- Highlight key differences between {language} and {known_language} for this concept
- Include a "comparison_to_known" field with a brief note like: "Similar to Python's 'with' statement but requires explicit IDisposable"
"""
        
        # Add context if provided
        context_section = ""
        if context:
            context_section = f"""
Context of what the student is trying to do:
{context}

Tailor your example to be relevant to their use case.
"""
        
        return f"""You are helping a student learn the concept of "{concept}" in {language}.

{context_section}
{comparison_section}

TASK:
Generate a clear, working code example for "{concept}".

Example Type: {example_type}
Expected Length: {example_length}

{length_instruction}

REQUIREMENTS:
1. Code must be COMPLETE and RUNNABLE (or a valid syntax template for basic concepts)
2. Use descriptive variable names
3. Include brief inline comments explaining key parts
4. Make it practical and realistic (not foo/bar examples)
5. Keep it focused on ONLY this concept

EXAMPLE FORMATS:

For BASIC concepts (1-3 lines):
```
for(int i = 0; i < n; i++) {{
    // Your code here
}}
```

For INTERMEDIATE concepts (5-10 lines):
```
public void ProcessData(List<int> numbers) {{
    foreach(int num in numbers) {{
        if(num > 0) {{
            Console.WriteLine($"Positive: {{num}}");
        }}
    }}
}}
```

For ADVANCED concepts (10-15 lines):
```
private static object lockObj = new object();
private static int counter = 0;

public static void IncrementCounter() {{
    lock(lockObj) {{
        counter++;
        Console.WriteLine($"Counter: {{counter}}");
    }}
}}

// This demonstrates thread-safe counter increments
```

Return ONLY a valid JSON object with this structure:
{{
    "code_example": "the working code example with \\n for newlines",
    "explanation": "2-3 sentence explanation of what the example shows and key points",
    "comparison_to_known": "optional comparison to {known_language if known_language else 'null'}"
}}

CRITICAL:
- Response must be ONLY valid JSON
- No markdown code blocks
- Use \\n for newlines in code_example string
- Escape all quotes properly
- Start with {{ and end with }}

EXAMPLE VALID RESPONSE:
{{"code_example": "for(int i = 0; i < 10; i++) {{\\n    Console.WriteLine(i);\\n}}", "explanation": "A basic for loop that iterates from 0 to 9", "comparison_to_known": null}}"""


# Singleton instance
_concept_example_agent = None

def get_concept_example_agent() -> ConceptExampleAgent:
    """Get the concept example agent singleton"""
    global _concept_example_agent
    if _concept_example_agent is None:
        _concept_example_agent = ConceptExampleAgent()
    return _concept_example_agent