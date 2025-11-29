"""
Prompt templates for all agents
Clean, focused prompts for each agent's specific task
"""

def get_test_generation_prompt(assignment_text: str, files: list, target_language: str) -> str:
    """
    Generate test cases based on assignment requirements (UPDATED FOR MULTI-FILE AND MULTI-CLASS)
    """
    # Build tasks summary from file structure
    tasks_summary = ""
    for file_data in files:
        filename = file_data.get('filename', 'unknown')
        tasks_summary += f"\n=== File: {filename} ===\n"

        # Handle simple file structure (tasks directly in file)
        if file_data.get('tasks') is not None:
            for task in file_data.get('tasks', []):
                tasks_summary += f"Task {task.get('id', '')}: {task.get('title', '')} - {task.get('description', '')}\n"

        # Handle multi-class file structure (classes with tasks)
        elif file_data.get('classes') is not None:
            for class_obj in file_data.get('classes', []):
                class_name = class_obj.get('class_name', 'Unknown')
                tasks_summary += f"\nClass: {class_name}\n"
                for task in class_obj.get('tasks', []):
                    tasks_summary += f"Task {task.get('id', '')}: {task.get('title', '')} - {task.get('description', '')}\n"

    return f"""You are a test case generator for programming assignments. Your task is to generate comprehensive test cases.

Assignment:
{assignment_text}

Tasks Breakdown by File:
{tasks_summary}

Target Language: {target_language}

Your task is to:
1. Analyze the assignment to identify functions/methods that need testing
2. Generate 5-15 test cases covering normal, edge, and error scenarios
3. Infer function signatures from the assignment description
4. Create realistic input/output pairs
5. Ensure tests are appropriate for the target language
6. If needed, add tests for each task or for each function within tasks so students can test a single function at a time.

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

TEMPLATE CODE DETECTION:
If the assignment includes existing template/skeleton code:
- EXTRACT the file and class structure from the template
- IDENTIFY variable names, method signatures, class names used in template
- PRESERVE these exact names - students must use them
- Organize tasks by which class they belong to

Example workflow:
If template shows:
public class BookingSystem {{
    private Order[] orderQueue;
    public void processBooking() {{ }}
}}
public class Order {{
    private int orderId;
    public int getOrderId() {{ }}
}}

You should detect:
- Two classes: BookingSystem, Order
- Variables to preserve: orderQueue (in BookingSystem), orderId (in Order)
- Methods to preserve: processBooking(), getOrderId()

MULTI-CLASS FILE ORGANIZATION:
For C#/Java files with multiple classes:

Detection patterns:
- Look for "public class ClassName" or "class ClassName"
- Look for "ClassName.methodName()" references
- Look for task descriptions mentioning class names

Confidence levels:
- HIGH: Template shows "public class Hotel" → use "Hotel"
- MEDIUM: Task says "Implement Hotel pricing" → use "Hotel"
- LOW: Task says "add pricing logic" → don't guess, use null

Only create class entries for HIGH confidence detections.

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

FOR SINGLE-CLASS OR SIMPLE FILES:
{{
    "overview": "Brief 2 sentence overview",
    "total_estimated_time": "X hours",
    "template_structure": {{
        "has_template": false,
        "variable_names": [],
        "class_names": []
    }},
    "files": [
        {{
            "filename": "main.py",
            "purpose": "Brief description",
            "classes": null,
            "tasks": [
                {{
                    "id": 1,
                    "title": "Short title",
                    "description": "What to do",
                    "dependencies": [],
                    "estimated_time": "X minutes",
                    "concepts": ["concept1", "concept2"]
                }}
            ]
        }}
    ]
}}

FOR MULTI-CLASS FILES WITH TEMPLATE:
{{
    "overview": "Brief 2 sentence overview",
    "total_estimated_time": "X hours",
    "template_structure": {{
        "has_template": true,
        "variable_names": ["orderQueue", "orderId", "userName"],
        "class_names": ["BookingSystem", "Order", "User"],
        "method_signatures": ["processBooking()", "getOrderId()"]
    }},
    "files": [
        {{
            "filename": "Program.cs",
            "purpose": "Multi-class booking system",
            "classes": [
                {{
                    "class_name": "BookingSystem",
                    "purpose": "Main booking logic",
                    "tasks": [
                        {{
                            "id": 1,
                            "title": "Initialize booking queue",
                            "description": "Set up orderQueue array",
                            "template_variables": ["orderQueue"],
                            "dependencies": [],
                            "estimated_time": "20 minutes",
                            "concepts": ["Arrays", "Initialization"]
                        }}
                    ]
                }},
                {{
                    "class_name": "Order",
                    "purpose": "Order data structure",
                    "tasks": [...]
                }}
            ],
            "tasks": null
        }}
    ]
}}

EXAMPLE 1 - Simple Python file (no template, no classes):
{{
    "overview": "Basic calculator with arithmetic operations",
    "total_estimated_time": "1.5 hours",
    "template_structure": {{
        "has_template": false,
        "variable_names": [],
        "class_names": []
    }},
    "files": [
        {{
            "filename": "calculator.py",
            "purpose": "Arithmetic operations",
            "classes": null,
            "tasks": [
                {{"id": 1, "title": "Create add function", "description": "...", "dependencies": [], "estimated_time": "15 minutes", "concepts": ["Functions"]}}
            ]
        }}
    ]
}}

EXAMPLE 2 - Multi-class C# file with template:
{{
    "overview": "Library management system with books and members",
    "total_estimated_time": "6 hours",
    "template_structure": {{
        "has_template": true,
        "variable_names": ["bookList", "memberId", "borrowDate"],
        "class_names": ["Library", "Book", "Member"],
        "method_signatures": ["addBook(Book b)", "getMemberId()"]
    }},
    "files": [
        {{
            "filename": "LibrarySystem.cs",
            "purpose": "Library management with multiple classes",
            "classes": [
                {{
                    "class_name": "Library",
                    "purpose": "Manages book collection",
                    "tasks": [
                        {{"id": 1, "title": "Initialize book list", "description": "Create bookList array", "template_variables": ["bookList"], "dependencies": [], "estimated_time": "20 minutes", "concepts": ["Collections"]}}
                    ]
                }},
                {{
                    "class_name": "Book",
                    "purpose": "Book data",
                    "tasks": [
                        {{"id": 2, "title": "Add book properties", "description": "...", "template_variables": [], "dependencies": [], "estimated_time": "15 minutes", "concepts": ["Classes"]}}
                    ]
                }},
                {{
                    "class_name": "Member",
                    "purpose": "Library member data",
                    "tasks": [
                        {{"id": 3, "title": "Create member ID getter", "description": "...", "template_variables": ["memberId"], "dependencies": [], "estimated_time": "10 minutes", "concepts": ["Encapsulation"]}}
                    ]
                }}
            ],
            "tasks": null
        }}
    ]
}}

CRITICAL RULES:
- Use "classes" array for multi-class files, set "tasks" to null
- Use "tasks" array for simple files, set "classes" to null
- NEVER use both classes and tasks at the same level
- Extract template variable names if template exists
- Task IDs must be unique across entire response
- Only detect classes with HIGH confidence

CRITICAL RESPONSE FORMAT:
- ONLY valid JSON, no markdown, no explanations
- Start with {{ and end with }}
- Must include "template_structure" field
- Task IDs unique across ALL files
- No code blocks, no comments"""



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


def get_file_codegen_prompt(tasks_data: list, filename: str,
                            class_structure: dict = None,
                            template_variables: list = None) -> str:
    """
    Generate prompt for creating ONE complete file with ALL its tasks.
    Focused approach for better quality than batch generation.

    Args:
        tasks_data: List of task dicts for THIS file only
        filename: Name of file being generated
        class_structure: Dict of {class_name: [tasks]} or None for single-class
        template_variables: List of variable names to preserve from template, or None
    """

    if not tasks_data:
        return ""

    # Determine language and comment style
    language = tasks_data[0].get('programming_language', 'python').lower()

    if language in ['python']:
        comment_style = '#'
        comment_example = '# TODO: Implement this'
    else:
        comment_style = '//'
        comment_example = '// TODO: Implement this'

    # Detect if multi-class file
    is_multi_class = class_structure and len(class_structure) > 1
    class_list = sorted(class_structure.keys()) if class_structure else []

    # Build structure guidance
    if is_multi_class:

        structure_guidance = f"""
MULTI-CLASS FILE - CRITICAL STRUCTURE:

This file requires {len(class_list)} separate classes: {', '.join(class_list)}

Required structure:
```
using System;

namespace YourNamespace
{{
    public class {class_list[0]}
    {{
        // All tasks for {class_list[0]} go here
    }}

    public class {class_list[1] if len(class_list) > 1 else 'SecondClass'}
    {{
        // All tasks for this class go here
    }}

    // ... additional classes
}}
```

RULES:
- Create exactly {len(class_list)} classes in this order: {', '.join(class_list)}
- Each task belongs to a specific class - check the task's class assignment
- Complete each class before starting the next
- All classes inside ONE namespace
- Methods MUST be inside classes - never at top level

Task distribution:"""
        for class_name in class_list:
            if class_name in class_structure:
                class_tasks_list = class_structure[class_name]
                task_ids = [str(i+1) for i, t in enumerate(tasks_data) if t.get('class_name') == class_name]
                structure_guidance += f"\n- {class_name}: tasks {', '.join(task_ids) if task_ids else 'check below'}"
    else:
        structure_guidance = f"""
SINGLE-CLASS FILE:
Generate ONE complete file with ONE main class containing all {len(tasks_data)} tasks.
Keep it simple and well-structured.
"""

    # Template variable preservation
    if template_variables:
        template_guidance = f"""
CRITICAL - TEMPLATE VARIABLE PRESERVATION:
This assignment includes a template with specific variable names.
YOU MUST use these EXACT variable names:
{', '.join(template_variables)}

NEVER rename these variables. Students are graded on using the correct names.
Examples:
- If template has "orderQueue", use "orderQueue" (not "queue" or "orders")
- If template has "memberId", use "memberId" (not "id" or "member_id")

Check each task for template_variables field and use those exact names.
"""
    else:
        template_guidance = ""

    # Build task descriptions
    tasks_description = ""
    for i, task in enumerate(tasks_data, 1):
        concepts_str = ", ".join(task.get('concepts', []))
        exp_level = task.get('experience_level', 'intermediate')
        target_class = task.get('class_name', 'Program')
        template_vars = task.get('template_variables', [])

        tasks_description += f"""
=== TASK {i} ===
Target Class: {target_class}
Description: {task['task_description']}
Concepts: {concepts_str}
Experience Level: {exp_level}
"""

        if template_vars:
            tasks_description += f"MUST use these variable names: {', '.join(template_vars)}\n"

    # C#/Java specific structure guidance
    file_structure_guidance = ""
    if language in ['csharp', 'c#', 'java']:
        file_structure_guidance = f"""

CRITICAL C#/JAVA FILE STRUCTURE:
This is ONE file ({filename}) that contains ALL {len(tasks_data)} tasks.

YOU MUST:
1. Generate ONE namespace/package declaration at the TOP
2. Generate ONE class definition  
3. Put ALL methods, fields, and logic from ALL {len(tasks_data)} tasks INSIDE this ONE class
4. Do NOT create separate class definitions for each task
5. Do NOT repeat namespace or using statements for each task

CORRECT STRUCTURE for {len(tasks_data)} tasks:
```csharp
using System;
using System.Xml;
// ... all necessary imports at top

namespace ConsoleApp1
{{
    public class Program
    {{
        // ===== TASK 1 =====
        // Fields/methods from task 1
        
        // ===== TASK 2 =====
        // Fields/methods from task 2
        
        // ===== TASK 3 =====
        // Fields/methods from task 3
        
        // ... all tasks integrated in ONE class
    }}
}}
```

WRONG - NEVER DO THIS:
```csharp
// ===== TASK 1 =====
namespace App {{ class Program {{ }} }}

// ===== TASK 2 =====
namespace App {{ class Program {{ }} }}  ← DUPLICATE CLASS! COMPILATION ERROR!
```

Generate ONE complete, compilable {filename} with ALL tasks integrated into ONE class.
"""

    return f"""Generate scaffolding for ONE complete file in a programming assignment.

FILE: {filename}
LANGUAGE: {language}
NUMBER OF TASKS: {len(tasks_data)}

{structure_guidance}

{template_guidance}

Tasks for this file:
{tasks_description}

CRITICAL REQUIREMENTS:
1. Generate ONE complete, valid, compilable file: {filename}
2. {"Create all " + str(len(class_list)) + " classes with proper structure" if is_multi_class else "Use proper single-class structure"}
3. {"Each task goes in its assigned class" if is_multi_class else "All tasks in one class"}
4. Use CONSISTENT variable names throughout this ENTIRE file
5. Proper {language} syntax
6. Comment style: Use "{comment_style}" for ALL comments and TODOs
7. Example: {comment_example}

LANGUAGE-SPECIFIC RULES:
{"- NEVER use # for comments in this language (causes compilation errors)" if comment_style == '//' else ""}
{"- MUST include ONE namespace with ALL " + str(len(class_list)) + " classes inside it" if is_multi_class and language in ['csharp', 'c#', 'java'] else ""}
{"- MUST include ONE class with all tasks inside it" if not is_multi_class and language in ['csharp', 'c#', 'java'] else ""}
{"- C/C++: Include necessary headers (#include) at top" if language in ['c', 'c++', 'cpp'] else ""}
{"- Python: Include imports at top" if language == 'python' else ""}
{file_structure_guidance}

VARIABLE NAMING - CRITICAL:
{"- YOU MUST use the EXACT variable names from the template: " + ", ".join(template_variables) if template_variables else ""}
{"- NEVER rename template variables (e.g., don't change 'orderQueue' to 'queue')" if template_variables else ""}
- When you introduce NEW variables, choose clear names
- Use that EXACT same name in ALL tasks throughout this file
- NEVER rename variables between tasks (e.g., don't change "shared_buffer" to "buffer")
- Consistency is CRITICAL for student learning

EXPERIENCE LEVEL GUIDANCE:
For EACH task, generate appropriate number of TODOs based on experience level:

- Beginner (5-8 TODOs per task):
  * Provide MORE granular step-by-step TODOs
  * Include function/method signatures with parameter types
  * Add helpful inline comments and hints
  * Break down complex logic into smaller steps
  * Example: "TODO: Create variable X", "TODO: Loop through items", "TODO: Check if condition", "TODO: Update result"

- Intermediate (3-5 TODOs per task):
  * Moderate guidance with clear TODO markers
  * Provide structure but let student implement logic
  * TODOs at function/section level, not line-by-line
  * Student figures out the details within each TODO
  * Example: "TODO: Implement input validation", "TODO: Process data", "TODO: Return result"

- Advanced (1-3 TODOs per task):
  * Minimal scaffolding with high-level TODOs only
  * Assume student knows patterns and can break down problems
  * TODOs mark major sections/components only
  * Student implements everything with minimal guidance
  * Example: "TODO: Implement the main algorithm", "TODO: Handle edge cases"

CRITICAL: Adjust TODO count per task based on experience_level field!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL JSON RESPONSE FORMAT - READ CAREFULLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your response MUST be ONLY valid JSON in this EXACT format:

{{
    "tasks": [
        {{
            "task_number": 1,
            "filename": "{filename}",
            "code_snippet": "code here with \\n for newlines",
            "instructions": "brief guidance",
            "todos": ["todo 1", "todo 2", "todo 3"]
        }},
        {{
            "task_number": 2,
            "filename": "{filename}",
            "code_snippet": "code here with \\n for newlines",
            "instructions": "brief guidance",
            "todos": ["todo 1", "todo 2"]
        }}
    ]
}}

ABSOLUTE REQUIREMENTS:
1. Start your response with {{ (opening brace)
2. End your response with }} (closing brace)
3. NO markdown formatting (no ```, no ```json, no ```csharp)
4. NO explanations before or after the JSON
5. NO code comments outside the JSON structure
6. Include ALL {len(tasks_data)} tasks in the "tasks" array
7. Use \\n for newlines inside code_snippet strings
8. Escape all quotes inside strings with \\"
9. Use {comment_style} for comments inside the code
10. For C#/Java: Generate ONE complete class with all methods inside

WRONG - DO NOT DO THIS:
```json
{{ ... }}
```

CORRECT - DO THIS:
{{ ... }}

Your ENTIRE response must be parseable by JSON.parse(). Nothing else.

Generate the JSON now:"""