"""
Prompt templates for all agents
Clean, focused prompts for each agent's specific task
"""

def get_test_generation_prompt(assignment_text: str, files: list, target_language: str) -> str:
    """
    Generate test cases based on assignment requirements (UPDATED FOR MULTI-FILE)
    """
    # Build tasks summary from file structure
    tasks_summary = ""
    for file_data in files:
        filename = file_data.get('filename', 'unknown')
        tasks_summary += f"\n=== File: {filename} ===\n"
        for task in file_data.get('tasks', []):
            tasks_summary += f"Task {task.get('id', '')}: {task.get('title', '')} - {task.get('description', '')}\n"

    return f"""You are a test case generator for programming assignments. Your task is to generate comprehensive test cases.

Assignment:
{assignment_text}

Tasks Breakdown by File:
{tasks_summary}

Target Language: {target_language}

Your task is to:
1. Analyze the assignment to identify functions/methods that need testing
2. Generate 3-7 test cases covering normal, edge, and error scenarios
3. Infer function signatures from the assignment description
4. Create realistic input/output pairs
5. Ensure tests are appropriate for the target language

TEST CASE DISTRIBUTION:
- 60% normal cases (typical usage)
- 30% edge cases (boundary conditions, empty inputs, single elements)
- 10% error cases (invalid inputs, type errors)

LANGUAGE-SPECIFIC FORMATTING:
Format inputs and outputs according to the target language:
- Python: Use Python syntax (e.g., "True", "False", "None", "[]", "{{}}")
- Java: Use Java syntax (e.g., "true", "false", "null", "new ArrayList<>()")
- JavaScript: Use JS syntax (e.g., "true", "false", "null", "[]", "{{}}")
- C++: Use C++ syntax (e.g., "true", "false", "nullptr", "vector<int>()")

FUNCTION NAME INFERENCE:
- Look for explicit function names in the assignment (e.g., "Write a function called reverse_string")
- If not explicit, infer from the task description (e.g., "reverse string" → "reverse_string" or "reverseString")
- Use appropriate naming convention for the language (snake_case for Python, camelCase for Java/JS/C++)

EXAMPLE TEST CASE:
For assignment: "Write a function is_palindrome(s) that checks if a string is a palindrome"
{{
  "test_name": "test_basic_palindrome",
  "function_name": "is_palindrome",
  "input_data": "\\"racecar\\"",
  "expected_output": "True",
  "description": "Basic palindrome check with simple word",
  "test_type": "normal"
}}

Return ONLY a valid JSON array of test case objects with this EXACT structure:
[
  {{
    "test_name": "descriptive_test_name",
    "function_name": "function_being_tested",
    "input_data": "input as string",
    "expected_output": "expected output as string",
    "description": "Human-readable description",
    "test_type": "normal|edge|error"
  }}
]

CRITICAL RESPONSE FORMAT:
- Your response must be ONLY valid JSON array
- Do NOT wrap in markdown code blocks (no ``` or ```json)
- Do NOT include any explanation before or after the JSON
- Ensure all strings are properly escaped
- Start your response with [ and end with ]
- Generate 3-7 test cases minimum
- If assignment is unclear, make reasonable assumptions and generate basic tests

EXAMPLE VALID RESPONSE:
[{{"test_name": "test_empty_input", "function_name": "reverse_string", "input_data": "\\"\\"", "expected_output": "\\"\\"", "description": "Handle empty string", "test_type": "edge"}}]"""


def get_parser_prompt(assignment_text: str, target_language: str,
                      known_language: str, experience_level: str) -> str:
    """
    Agent 1: Assignment Parser (UPDATED FOR MULTI-FILE)
    Parse assignment and break into ordered tasks organized by files
    """
    known_lang_context = f"\nKnown Language: {known_language}" if known_language else "\nNo prior programming experience"

    return f"""You are an educational AI assistant that helps students learn programming by breaking down complex assignments.

Assignment Text:
{assignment_text}

Target Language: {target_language}
Student Experience Level: {experience_level}{known_lang_context}

Your task is to:
1. Identify all files that need to be created for this assignment
2. For each file, parse and identify required tasks
3. Order tasks by logical dependencies (what must be done first)
4. Break down complex tasks into smaller, manageable subtasks
5. Estimate time for each task (be realistic)
6. Identify key programming concepts for each task

IMPORTANT RULES:
- Do NOT provide complete solutions or full implementations
- Focus on breaking down WHAT needs to be done, not HOW to do it completely
- Ensure dependencies are realistic (task 3 cannot depend on task 5)
- Order tasks in a logical learning progression
- Each task should be completable in one sitting (20-40 minutes typically)
- If assignment requires multiple files, organize tasks by file
- If assignment is single-file, still return one file in the structure

FILE IDENTIFICATION GUIDELINES:
- Look for explicit file mentions in the assignment (e.g., "Create main.py and utils.py")
- Infer logical file separation (e.g., separate config, main logic, utilities)
- For simple assignments, one file is fine
- Include proper file extensions based on target language

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

Return ONLY a valid JSON object with this EXACT structure:
{{
    "overview": "Brief 2 sentence overview of the assignment",
    "total_estimated_time": "X hours",
    "files": [
        {{
            "filename": "main.py",
            "purpose": "Brief description of this file's role",
            "tasks": [
                {{
                    "id": 1,
                    "title": "Short descriptive title",
                    "description": "What needs to be accomplished in this task",
                    "dependencies": [],
                    "estimated_time": "X minutes",
                    "concepts": ["specific_concept1", "specific_concept2"]
                }}
            ]
        }}
    ]
}}

EXAMPLES:
Single-file: {{"overview": "...", "total_estimated_time": "2 hours", "files": [{{"filename": "calculator.py", "purpose": "Main calculator", "tasks": [{{"id": 1, "title": "...", "description": "...", "dependencies": [], "estimated_time": "30 minutes", "concepts": ["Functions"]}}]}}]}}

Multi-file: {{"overview": "...", "total_estimated_time": "8 hours", "files": [{{"filename": "server.py", "purpose": "...", "tasks": [{{"id": 1, ...}}]}}, {{"filename": "client.py", "purpose": "...", "tasks": [{{"id": 2, ...}}]}}]}}

CRITICAL RESPONSE FORMAT:
- ONLY valid JSON, no markdown, no explanations
- Start with {{ and end with }}
- Task IDs unique across ALL files
- No code blocks, no comments"""



def get_batch_codegen_prompt(tasks_data: list) -> str:
    """
    Agent 2: Batch Code Generator (UPDATED FOR MULTI-FILE)
    Generate starter code templates for multiple tasks in a single API call.

    Args:
        tasks_data: List of task dictionaries with task_description, programming_language, concepts, known_language, filename

    Returns:
        Prompt string for batch code generation
    """

    # Build descriptions for all tasks
    tasks_description = ""
    for i, task in enumerate(tasks_data, 1):
        concepts_str = ", ".join(task.get('concepts', []))
        known_lang = task.get('known_language')
        known_lang_note = f" (Student knows {known_lang})" if known_lang else ""
        filename = task.get('filename', 'unknown.py')

        tasks_description += f"""
=== TASK {i} ===
Filename: {filename}
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
8. Each task belongs to a specific file - include the filename in the response

Return ONLY a valid JSON object with this EXACT structure:
{{
    "tasks": [
        {{
            "task_number": 1,
            "filename": "the filename this task belongs to",
            "code_snippet": "the complete starter code template with TODO comments and \\n for newlines",
            "instructions": "brief instructions on how to approach completing the TODOs",
            "todos": ["list of TODO items in the order they should be completed"]
        }},
        {{
            "task_number": 2,
            "filename": "the filename this task belongs to",
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
- Include the filename field for each task
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
- Each task must include the filename field
- No code blocks or extra formatting"""



def get_helper_prompt(task_description: str, concepts: list, student_code: str,
                      question: str, previous_hints: list, help_count: int, 
                      known_language: str = None, target_language: str = None, experience_level: str = "intermediate") -> str:
    """
    Agent 3: Live Coding Helper (SMART CONTEXT-AWARE VERSION)
    Provide contextual hints based on student's struggle level
    NOW: Better parsing of student's question to identify which TODO they're stuck on
    """
    concepts_str = ", ".join(concepts)
    previous_hints_str = "\n".join([f"- {hint}" for hint in previous_hints]) if previous_hints else "None"
    # experiece context for experience based hints
    experience_context = ""
    if experience_level.lower() == "beginner":
        experience_context = """

STUDENT EXPERIENCE: Beginner
- Use simpler language and avoid jargon
- Explain concepts more thoroughly
- Use more concrete examples
- Break down steps into smaller pieces
- Be extra patient and encouraging"""
    elif experience_level.lower() == "advanced":
        experience_context = """

STUDENT EXPERIENCE: Advanced
- You can use technical terminology
- Hints can be more concise
- LESS TEST CASES THAN INTERMEDIATE
- Assume familiarity with common patterns
- Focus on subtle issues or optimizations
- Less hand-holding needed"""
    else:  # intermediate
        experience_context = """

STUDENT EXPERIENCE: Intermediate
- Balance between explanation and brevity
- Use technical terms but explain if uncommon
- LESS TEST CASES THAN BEGINNER
- Assume basic programming knowledge
- Standard hint depth"""
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
- DO NOT show code examples yet
- DO NOT ask questions back to the student
- If they haven't implemented anything yet, suggest a starting point rather than asking a question back.
- Same way if they have implemented eveything correctly, just give them a nudge forward.
- DO NOT end with "What specific hint are you asking?" or similar phrases"""
        
    elif help_count == 2:
        hint_level = "moderate"
        hint_instruction = """Provide a more specific hint with guidance on the approach.
- Explain the approach in pseudocode or plain English
- Show a SIMILAR example (different variable names, different context)
- Point out what's missing or incorrect in their approach
- You can show small code snippets (3-5 lines) but not the full solution
- DO NOT ask questions back to the student
- DO NOT end with "Does this help?" or similar phrases"""
        
    else:  # 3+
        hint_level = "strong"
        hint_instruction = """Provide a detailed hint that's close to the solution but still requires them to implement it.
- Show a similar working example with DIFFERENT context
- Explain the logic step-by-step
- You can show larger code examples but use different variable names and slightly different scenario
- Still leave some implementation work for them (don't just give the exact answer)
-DO NOT ask questions back to the student
- DO NOT end with "Any questions?" or similar phrases"""
    

    code_analysis_section = f"""
CONTEXT AWARENESS (Internal analysis - do not verbalize this to student):
1. Identify which TODO they're stuck on from their question
2. See what code they've written vs what's missing
3. Target your hint ONLY to the specific part they asked about

YOUR RESPONSE RULES:
- If code is empty: Give ONE nudge to start, then STOP
- If code is correct: Acknowledge and tell them to move on, then STOP  
- If specific error: Point it out with fix example, then STOP
- Otherwise: Give targeted hint for their question, then STOP
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
10. Use IMPERATIVE/DIRECTIVE language ("Create X", "Add Y") 
NOT observational language ("I see...", "You're trying...")

CRITICAL: HOW TO END YOUR HINT
✅ Give your hint, be encouraging, then STOP
✅ Use statements, not questions
✅ Format: [Hint] + [Brief encouragement] + END

❌ DO NOT end with questions like:
   - "What do you think?"
   - "Does this help?"
   - "Do you understand?"
   - "Want me to explain more?"
   - "Any other questions?"

❌ DO NOT invite further conversation

SPECIAL CASES:

IF student's code is EMPTY or just TODOs:
- Tell them to start with the first TODO
- Give one small nudge about the first step
- Example: "Start by creating a variable to store X. Then move to the next TODO."
- STOP - no questions

IF student's code looks CORRECT for the current TODO:
- Acknowledge it's correct
- Tell them to move to the next TODO or task
- Example: "This looks correct! You've handled X properly. Move on to the next TODO."
- STOP - no questions

IF student has a specific error or question:
- Answer their question directly
- Show relevant example if needed
- Example: "The error is because X. Here's the fix: [example]. Try this approach."
- STOP - no questions

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
        return false;
    }}
    
    if (!availableTickets.Contains(ticketId)) {{
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