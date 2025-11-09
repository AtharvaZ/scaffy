"""
Prompt templates for all three agents
Clean, focused prompts for each agent's specific task
"""

def get_parser_prompt(assignment_text: str, target_language: str, 
                      known_language: str, experience_level: str) -> str:
    """
    Agent 1: Assignment Parser (UPDATED)
    Parse assignment and break into ordered tasks with dependencies
    """
    known_lang_context = f"\nKnown Language: {known_language}" if known_language else "\nNo prior programming experience"
    
    return f"""You are an educational AI assistant that helps students learn programming by breaking down complex assignments.

Assignment Text:
{assignment_text}

Target Language: {target_language}
Student Experience Level: {experience_level}{known_lang_context}

Your task is to:
1. Parse the assignment and identify all required tasks
2. Order tasks by logical dependencies (what must be done first)
3. Break down complex tasks into smaller, manageable subtasks
4. Estimate time for each task (be realistic)
5. Identify key programming concepts for each task

IMPORTANT RULES:
- Do NOT provide complete solutions or full implementations
- Focus on breaking down WHAT needs to be done, not HOW to do it completely
- Ensure dependencies are realistic (task 3 cannot depend on task 5)
- Order tasks in a logical learning progression
- Each task should be completable in one sitting (20-40 minutes typically)

CONCEPT IDENTIFICATION GUIDELINES:
When identifying concepts for each task, be SPECIFIC and distinguish between:
- Basic concepts (loops, conditionals, variables) - these are universal
- Language-specific features (LINQ, async/await, delegates, generics)
- Advanced patterns (threading, concurrency, design patterns)
- Framework-specific (WPF, ASP.NET, specific libraries)

Good concept examples:
- "Threading" not just "multithreading"
- "Thread Safety" and "Locks" as separate concepts
- "LINQ queries" not just "data processing"
- "Async/await pattern" not just "asynchronous programming"
- "Lambda expressions" as a distinct concept
- "Delegates/Events" when applicable

This helps the next agent (code generator) determine which concepts need examples based on the student's background.

Return ONLY a valid JSON object with this EXACT structure:
{{
    "overview": "Brief 2 sentence overview of the assignment",
    "total_estimated_time": "X hours",
    "tasks": [
        {{
            "id": 1,
            "title": "Short descriptive title",
            "description": "What needs to be accomplished in this task",
            "dependencies": [],
            "estimated_time": "X minutes",
            "concepts": ["specific_concept1", "specific_concept2", "language_feature"]
        }}
    ]
}}

EXAMPLE (good concept specificity):
{{
    "tasks": [
        {{
            "id": 1,
            "concepts": ["File I/O", "StreamReader", "using statement"]
        }},
        {{
            "id": 2,
            "concepts": ["Threading", "Thread Safety", "Locks", "Shared state management"]
        }},
        {{
            "id": 3,
            "concepts": ["LINQ queries", "Lambda expressions", "IEnumerable"]
        }}
    ]
}}

CRITICAL RESPONSE FORMAT:
- Your response must be ONLY valid JSON
- Do NOT wrap in markdown code blocks (no ``` or ```json)
- Do NOT include any explanation before or after the JSON
- Do NOT include comments in the JSON
- Ensure all strings are properly escaped
- Ensure all JSON brackets and braces are balanced
- Start your response with {{ and end with }}

EXAMPLE VALID RESPONSE:
{{"overview": "Brief description", "total_estimated_time": "2 hours", "tasks": [{{"id": 1, "title": "Task 1", "description": "Do X", "dependencies": [], "estimated_time": "30 minutes", "concepts": ["concept1"]}}]}}

INVALID RESPONSES (DO NOT DO THIS):
```json
{{"tasks": []}}
```

Here's the JSON:
{{"tasks": []}}

{{"tasks": []}} // This is the breakdown"""


# backend/utils/agent_prompts.py

# Add this new function at the end of the file

def get_batch_codegen_prompt(tasks_data: list) -> str:
    """
    Agent 2: Batch Code Generator
    Generate starter code templates for multiple tasks in a single API call.
    
    Args:
        tasks_data: List of task dictionaries with task_description, programming_language, concepts, known_language
        
    Returns:
        Prompt string for batch code generation
    """
    
    # Build descriptions for all tasks
    tasks_description = ""
    for i, task in enumerate(tasks_data, 1):
        concepts_str = ", ".join(task.get('concepts', []))
        known_lang = task.get('known_language')
        known_lang_note = f" (Student knows {known_lang})" if known_lang else ""
        
        tasks_description += f"""
=== TASK {i} ===
Description: {task['task_description']}
Language: {task['programming_language']}
Concepts: {concepts_str}{known_lang_note}

"""
    
    return f"""You are generating starter code templates for multiple tasks in a programming assignment.

Generate starter code for ALL {len(tasks_data)} tasks below in ONE response.

{tasks_description}

CRITICAL RULES FOR ALL TASKS:
1. Generate ONLY code templates with proper structure
2. Include function/method signatures but NO implementations
3. Add clear TODO comments explaining what each part should do
4. Include necessary imports and basic setup
5. Do NOT implement the actual logic - that's for the student to learn!
6. Do NOT generate concept examples - they are generated on-demand when requested
7. Always set concept_examples to null

Return ONLY a valid JSON object with this EXACT structure:
{{
    "tasks": [
        {{
            "task_number": 1,
            "code_snippet": "the complete starter code template with TODO comments and \\n for newlines",
            "instructions": "brief instructions on how to approach completing the TODOs",
            "todos": ["list of TODO items in the order they should be completed"]
        }},
        {{
            "task_number": 2,
            "code_snippet": "...",
            "instructions": "...",
            "todos": [...]
        }}
        // ... continue for all {len(tasks_data)} tasks
    ]
}}

IMPORTANT:
- Generate code for ALL {len(tasks_data)} tasks
- Each code_snippet should be 10-30 lines (concise templates)
- Use \\n for newlines in code_snippet strings
- Keep instructions brief (2-3 sentences)
- Include 2-4 TODO items per task
- Do NOT wrap in markdown code blocks
- Response must be ONLY valid JSON
- Start with {{ and end with }}
- Escape all quotes and backslashes properly

EXAMPLE TODO COMMENT STYLE:
// TODO: Implement input validation here
// TODO: Create a loop to process each item
// TODO: Call the helper function and store the result

CRITICAL RESPONSE FORMAT:
- Response must be ONLY valid JSON
- No markdown, no explanations, just JSON
- All {len(tasks_data)} tasks must be included
- No code blocks or extra formatting"""



def get_helper_prompt(task_description: str, concepts: list, student_code: str,
                      question: str, previous_hints: list, help_count: int, 
                      known_language: str = None, target_language: str = None) -> str:
    """
    Agent 3: Live Coding Helper (SMART CONTEXT-AWARE VERSION)
    Provide contextual hints based on student's struggle level
    NOW: Better parsing of student's question to identify which TODO they're stuck on
    """
    concepts_str = ", ".join(concepts)
    previous_hints_str = "\n".join([f"- {hint}" for hint in previous_hints]) if previous_hints else "None"
    
    # Language context for better hints
    language_context = ""
    if known_language and target_language:
        language_context = f"""

LANGUAGE CONTEXT:
Student knows: {known_language}
Learning: {target_language}

When providing hints or examples, you can reference {known_language} patterns to help bridge understanding.
For example: "Think of this like Python's 'with' statement" or "Similar to C++'s RAII pattern"
"""
    
    # Determine hint level based on help count
    if help_count == 1:
        hint_level = "gentle"
        hint_instruction = """Give a high-level conceptual hint. Help them think about the problem differently.
- Ask guiding questions
- Point them to the right direction without giving away the answer
- Remind them of relevant concepts they should consider
- DO NOT show code examples yet"""
        
    elif help_count == 2:
        hint_level = "moderate"
        hint_instruction = """Provide a more specific hint with guidance on the approach.
- Explain the approach in pseudocode or plain English
- Show a SIMILAR example (different variable names, different context)
- Point out what's missing or incorrect in their approach
- You can show small code snippets (3-5 lines) but not the full solution"""
        
    else:  # 3+
        hint_level = "strong"
        hint_instruction = """Provide a detailed hint that's close to the solution but still requires them to implement it.
- Show a similar working example with DIFFERENT context
- Explain the logic step-by-step
- You can show larger code examples but use different variable names and slightly different scenario
- Still leave some implementation work for them (don't just give the exact answer)"""
    
    # NEW: Analyze the student's code and question to identify context
    code_analysis_section = f"""
ANALYZE THE STUDENT'S SITUATION:
1. Look at their code to see how far they've gotten
2. Look for TODO comments to see what they haven't implemented yet
3. Their question might reference a specific TODO or part of the task
4. If their question is "I'm stuck on: [specific TODO text]", focus your hint on THAT specific part

SMART CONTEXT DETECTION:
- If you see "// TODO: Validate room number" in their code AND they're asking about validation, focus on that
- If multiple TODOs remain, prioritize the one they're asking about
- Look at what they've already implemented successfully - don't repeat hints about those parts
- If they're stuck on line X, look at the surrounding code context
"""
    
    return f"""You are a live coding assistant helping a student who is stuck while programming.

Task Goal: {task_description}
Concepts: {concepts_str}{language_context}

Student's Current Code:
```
{student_code}
```

Student's Question: {question}

Previous Hints Given:
{previous_hints_str}

Times Asked for Help on This Section: {help_count}
Hint Level: {hint_level}

{code_analysis_section}

INSTRUCTIONS:
{hint_instruction}

CRITICAL RULES:
1. Do NOT give them the complete solution to THEIR specific task
2. Help them learn by guiding their thinking, not doing it for them
3. Use examples with DIFFERENT context (different variable names, slightly different problem)
4. If showing code, use a SIMILAR but NOT IDENTICAL scenario
5. Do not repeat previous hints - build on them and go deeper
6. Be encouraging and supportive - struggling is part of learning!
7. If they have a syntax error or misunderstanding, you can point it out directly
8. **FOCUS on the SPECIFIC part they're asking about, not the entire task**
9. **If you can identify which TODO they're stuck on from their code/question, address ONLY that TODO**

SMART HINT TARGETING:
- If question mentions "validate" or "validation" → Focus on input validation logic
- If question mentions "check" or "available" → Focus on checking data structures
- If question mentions "lock" or "thread" → Focus on thread safety
- If question is vague but you see incomplete TODOs in code → Guide them to the next logical TODO

EXAMPLE HINT PROGRESSION:

Hint 1 (gentle): "I see you're working on room validation. Think about how you'd check if a number is within a valid range. What data structure would help you keep track of available rooms?"

Hint 2 (moderate): "For validating the room number, you'll want to check two things: 1) Is it a positive number? 2) Does it exist in your available rooms list. Here's a similar pattern for validating an ID:
```
if (id < 1 || id > maxId) {{
    return false;  // Invalid
}}
```"

Hint 3 (strong): "Here's an example of validation with a ticket system (apply this same logic to room validation):
```
public bool ValidateTicket(int ticketId) {{
    if (ticketId < 1 || ticketId > totalTickets) {{
        Console.WriteLine("Invalid ticket ID");
        return false;
    }}
    
    if (!availableTickets.Contains(ticketId)) {{
        Console.WriteLine("Ticket not available");
        return false;
    }}
    
    return true;
}}
```
Apply this pattern to validate your room number."

Return ONLY a valid JSON object with this EXACT structure:
{{
    "hint": "Your helpful hint text here",
    "hint_type": "{hint_level}_hint",
    "example_code": "optional example code if relevant (or null)"
}}

CRITICAL RESPONSE FORMAT:
- Your response must be ONLY valid JSON
- Do NOT wrap in markdown code blocks (no ``` or ```json)
- Do NOT include any explanation before or after the JSON
- If including example_code, use \\n for newlines within the string
- Ensure all strings are properly escaped
- Start your response with {{ and end with }}

EXAMPLE VALID RESPONSE:
{{"hint": "Try using a loop here", "hint_type": "gentle_hint", "example_code": null}}"""