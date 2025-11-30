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

LANGUAGE-SPECIFIC FORMATTING AND TEST STYLES:

Python/JavaScript:
- Format inputs/outputs with proper syntax (e.g., "True", "False", "None", "[]")
- Use direct function calls: function_name(input)

C#/Java (for complex code with threading, classes, state):
- Use reflection-based or integration-style tests
- For simple functions: direct calls work
- For complex assignments (threading, multi-class, state management):
  * Generate tests that instantiate classes and call methods
  * Test observable behavior (output, state changes, file creation)
  * Use Main method to set up, execute, and verify behavior
  * Example test for threading: Check if threads created, if output contains expected patterns

CRITICAL - Detecting if code will have Main method:
- Threading assignments → Will have Main, use function_name: "Main"
- Console applications → Will have Main, use function_name: "Main"
- Assignments with "create a program" → Will have Main, use function_name: "Main"
- Kernel modules, drivers → Will have Main/init, use function_name: "Main"
- Simple utility functions → NO Main, use function_name: "ClassName.MethodName" or just "MethodName"

C#/Java Test Decision Tree:
1. Simple function (pure, stateless) → Direct call: `var result = FunctionName(input);`
2. Class with state → Instantiate and test: `var obj = new ClassName(); obj.Method(); Console.WriteLine(obj.Property);`
3. Threading/async → Test observable effects: Check console output for thread messages, completion markers
4. File I/O → Test if files created/modified correctly
5. Complex integration → Run Main() and verify complete program output

For threading/concurrent assignments in C#/Java:
- Don't test internal thread details (can't access thread objects easily)
- Test OBSERVABLE behavior:
  * Console output contains expected patterns
  * Expected number of messages
  * Synchronization correctness (no race conditions in output)
  * Completion markers ("All producers finished", etc.)

FUNCTION NAME INFERENCE:
- Look for explicit function names in the assignment (e.g., "Write a function called reverse_string")
- If not explicit, infer from the task description (e.g., "reverse string" → "reverse_string" or "reverseString")
- Use appropriate naming convention for the language (snake_case for Python, camelCase for Java/JS/C++)

EXAMPLE TEST CASES:

Example 1 - Simple Python function:
{{
  "test_name": "test_basic_palindrome",
  "function_name": "is_palindrome",
  "input_data": "\\"racecar\\"",
  "expected_output": "True",
  "description": "Basic palindrome check with simple word",
  "test_type": "normal"
}}

Example 2 - C# threading assignment (observable behavior test):
{{
  "test_name": "test_producer_consumer_basic",
  "function_name": "Main",
  "input_data": "",
  "expected_output": "CONTAINS:Producer,Consumer,produced,consumed",
  "description": "Verify producer and consumer threads execute and produce expected output patterns",
  "test_type": "normal"
}}
Note: Use "CONTAINS:word1,word2,word3" format for tests that check if output contains certain patterns

Example 3 - C# class method test (with namespace):
{{
  "test_name": "test_booking_system_initialization",
  "function_name": "ConsoleApp1.BookingSystem.ProcessBooking",
  "input_data": "",
  "expected_output": "Booking processed successfully",
  "description": "Test that booking system initializes and processes bookings",
  "test_type": "normal"
}}
Note: For C# with namespaces, use format: Namespace.ClassName.MethodName

IMPORTANT FOR C# CODE WITH EXISTING MAIN METHOD:
- If student code already has a Main method, use function_name: "Main"
- The test runner will execute the whole program as-is
- For threading/integration tests, always use function_name: "Main"
- For specific method tests without Main, use: "Namespace.ClassName.MethodName"

Return ONLY a valid JSON array of test case objects with this EXACT structure:
[
  {{
    "test_name": "descriptive_test_name",
    "function_name": "function_or_method_being_tested",
    "input_data": "input as string (or empty for integration tests)",
    "expected_output": "expected output as string (use CONTAINS:pattern1,pattern2 for partial matches)",
    "description": "Human-readable description",
    "test_type": "normal|edge|error"
  }}
]

SPECIAL OUTPUT MATCHING FOR C#/Java COMPLEX TESTS:
- Exact match: "Expected output text" → Output must exactly match
- Pattern match: "CONTAINS:word1,word2,word3" → Output must contain all these words/phrases
- Count match: "COUNT:ThreadName:5" → Output must contain "ThreadName" exactly 5 times

CRITICAL - DETECTING AND TESTING NON-DETERMINISTIC CODE:

Non-deterministic code produces variable outputs across runs due to randomness, threading, or probability-based logic.
You MUST detect these patterns and use appropriate testing strategies:

DETECTION PATTERNS FOR NON-DETERMINISTIC CODE:

1. Random Number Generation:
   - Keywords: Random, random, rand, RandomNumberGenerator, Math.random, random.choice, random.randint
   - Patterns: `new Random()`, `random.Next()`, `Math.random()`, `random.choice()`, `rand()`
   - Examples: Credit card generation, dice rolls, random selection, lottery numbers

2. Threading/Concurrency:
   - Keywords: Thread, Task, async, await, Semaphore, lock, Monitor, mutex, pthread, goroutine
   - Patterns: `new Thread()`, `Thread.Start()`, `Task.Run()`, `async/await`, `lock()`, `Semaphore`
   - Examples: Producer-consumer, multi-threaded processing, parallel execution

3. Probability-Based Logic:
   - Patterns: `if random > 0.7`, `probability check`, `chance calculation`, `weighted selection`
   - Examples: 70% valid credit cards, conditional ordering based on chance, event simulation

4. Time-Dependent Behavior:
   - Keywords: DateTime, timestamp, Sleep, Delay, time.sleep, Timer
   - Patterns: `DateTime.Now`, `Thread.Sleep()`, execution timing varies
   - Examples: Timestamp logging, scheduled tasks, timeout handling

5. State Changes with Variable Order:
   - Patterns: Event-driven updates, message queues, buffer operations, callback execution
   - Examples: Event handlers firing in unpredictable order, async callbacks

TESTING STRATEGY FOR NON-DETERMINISTIC CODE:

When you detect ANY of the above patterns in the user's code:

1. DO NOT use exact output matching
2. USE "CONTAINS:pattern1,pattern2,pattern3" format
3. Test for PRESENCE of expected elements, not exact text or order
4. Focus on OBSERVABLE BEHAVIOR and PROGRAM CORRECTNESS, not specific values

EXAMPLES OF NON-DETERMINISTIC TEST CASES:

Example A - Random Credit Card Selection (DO NOT test exact card number):
{{
  "test_name": "test_credit_card_processing",
  "function_name": "Main",
  "input_data": "",
  "expected_output": "CONTAINS:Credit card,processed,Travel Agent",
  "description": "Verify credit card is randomly selected and processed (exact card number varies)",
  "test_type": "normal"
}}
❌ WRONG: "expected_output": "Credit card 1234-5678-9012-3456 processed"
✅ RIGHT: "expected_output": "CONTAINS:Credit card,processed"

Example B - Threading with Variable Message Order:
{{
  "test_name": "test_multithreaded_execution",
  "function_name": "Main",
  "input_data": "",
  "expected_output": "CONTAINS:Thread started,Thread completed,Processing,COUNT:Thread:5",
  "description": "Verify all 5 threads execute (order may vary due to scheduling)",
  "test_type": "normal"
}}
Note: Use COUNT: to verify expected number of threads without requiring specific order

Example C - Probability-Based Order Confirmation (DO NOT test exact outcome):
{{
  "test_name": "test_order_confirmation_probability",
  "function_name": "Main",
  "input_data": "",
  "expected_output": "CONTAINS:Travel Agent,Order,Hotel",
  "description": "Verify order processing logic executes (confirmation probability varies)",
  "test_type": "normal"
}}
Note: If confirmation only happens 30% of the time, don't require "Order confirmed" in output

Example D - Random Price Generation:
{{
  "test_name": "test_price_calculation",
  "function_name": "Main",
  "input_data": "",
  "expected_output": "CONTAINS:Price,$,Total",
  "description": "Verify pricing system generates valid prices (exact values vary)",
  "test_type": "normal"
}}
❌ WRONG: "expected_output": "Price: $150.00"
✅ RIGHT: "expected_output": "CONTAINS:Price,$"

Example E - Threading with Random Data (Hotel Booking System):
{{
  "test_name": "test_hotel_booking_multithreaded",
  "function_name": "Main",
  "input_data": "",
  "expected_output": "CONTAINS:Travel Agent,Hotel,Order,room,Credit card,COUNT:Travel Agent:5",
  "description": "Verify 5 travel agents and hotel thread coordinate bookings with random prices and cards",
  "test_type": "normal"
}}
Note: Tests coordination and communication, not specific random values

GENERAL RULES FOR NON-DETERMINISTIC CODE:

1. If code uses Random/random → Use CONTAINS: for any values generated randomly
2. If code uses Thread/async → Use CONTAINS: for any output that may arrive in variable order
3. If code has probability checks → Test that code executes, not that specific branch is taken
4. If code has timestamps → Use CONTAINS: for timestamp presence, not exact value
5. If code has state changes → Test final state properties, not intermediate values

ANTI-PATTERNS TO AVOID:

❌ Testing exact random numbers: "expected_output": "Random number: 42"
✅ Test random generation works: "expected_output": "CONTAINS:Random number"

❌ Testing thread execution order: "expected_output": "Thread 1\\nThread 2\\nThread 3"
✅ Test all threads execute: "expected_output": "COUNT:Thread:3"

❌ Testing probability outcomes: "expected_output": "Order confirmed" (when only 30% chance)
✅ Test logic executes: "expected_output": "CONTAINS:Order,processed"

❌ Testing exact timestamps: "expected_output": "2025-01-15 10:30:45"
✅ Test timestamp exists: "expected_output": "CONTAINS:2025,:"

CONFIDENCE CHECK - Before finalizing each test:
Ask yourself: "Will this test produce the SAME output every time the code runs?"
- If NO → Use CONTAINS: or COUNT: patterns
- If YES → Exact match is acceptable

When in doubt, prefer CONTAINS: over exact matching for robustness.

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
- 🚨 CRITICAL: Assign methods to their respective classes in BOTH places:
  1. Global template_structure.method_signatures (all methods)
  2. PER-CLASS in each class's method_signatures array (methods for that class ONLY)

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
- Methods to preserve globally: processBooking(), getOrderId()
- 🚨 BookingSystem class MUST have method_signatures: ["processBooking()"]
- 🚨 Order class MUST have method_signatures: ["getOrderId()"]

MULTI-CLASS FILE ORGANIZATION:
For C#/Java files with multiple classes:

Detection patterns:
- Look for "public class ClassName" or "class ClassName"
- Look for "ClassName.methodName()" references
- Look for task descriptions mentioning class names

🚨 CRITICAL RULE FOR CLASS DETECTION:
- If template code shows "public class ClassName", you MUST create a class entry for it
- EVERY class in the template MUST appear in your classes array
- Do NOT skip classes - if it's in the template, it's required
- Even classes with minimal code in template are needed for the structure

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
                    "method_signatures": ["processBooking()"],
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
                    "method_signatures": ["getOrderId()"],
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
                    "method_signatures": ["addBook(Book b)"],
                    "tasks": [
                        {{"id": 1, "title": "Initialize book list", "description": "Create bookList array", "template_variables": ["bookList"], "dependencies": [], "estimated_time": "20 minutes", "concepts": ["Collections"]}}
                    ]
                }},
                {{
                    "class_name": "Book",
                    "purpose": "Book data",
                    "method_signatures": [],
                    "tasks": [
                        {{"id": 2, "title": "Add book properties", "description": "...", "template_variables": [], "dependencies": [], "estimated_time": "15 minutes", "concepts": ["Classes"]}}
                    ]
                }},
                {{
                    "class_name": "Member",
                    "purpose": "Library member data",
                    "method_signatures": ["getMemberId()"],
                    "tasks": [
                        {{"id": 3, "title": "Create member ID getter", "description": "...", "template_variables": ["memberId"], "dependencies": [], "estimated_time": "10 minutes", "concepts": ["Encapsulation"]}}
                    ]
                }}
            ],
            "tasks": null
        }}
    ]
}}

EXAMPLE 3 - Multi-file assignment (C kernel module + Makefile):
{{
    "overview": "Producer-consumer kernel module with compilation setup",
    "total_estimated_time": "4 hours",
    "template_structure": {{
        "has_template": false,
        "variable_names": [],
        "class_names": []
    }},
    "files": [
        {{
            "filename": "producer_consumer.c",
            "purpose": "Kernel module implementation with producer-consumer logic",
            "classes": null,
            "tasks": [
                {{"id": 1, "title": "Module initialization", "description": "Create module init function", "dependencies": [], "estimated_time": "30 minutes", "concepts": ["Kernel modules", "Initialization"]}},
                {{"id": 2, "title": "Producer implementation", "description": "Implement producer threads", "dependencies": [1], "estimated_time": "45 minutes", "concepts": ["Threading", "Semaphores"]}},
                {{"id": 3, "title": "Consumer implementation", "description": "Implement consumer threads", "dependencies": [1], "estimated_time": "45 minutes", "concepts": ["Threading", "Semaphores"]}}
            ]
        }},
        {{
            "filename": "Makefile",
            "purpose": "Build configuration for compiling kernel module",
            "classes": null,
            "tasks": [
                {{"id": 4, "title": "Configure Makefile", "description": "Set up Makefile with obj-m, all, and clean targets for kernel module compilation", "dependencies": [], "estimated_time": "15 minutes", "concepts": ["Build systems", "Makefiles"]}}
            ]
        }}
    ]
}}

🚨 CRITICAL - TASK ASSIGNMENT TO FILES:
When you create multiple files, ensure each task goes to the CORRECT file:
- Tasks related to source code logic → source file (e.g., .c, .py, .java)
- Tasks related to building/compiling → Makefile/build file
- Tasks related to configuration → config file
- Tasks related to dependencies → package file (package.json, requirements.txt, etc.)

Example task assignments:
✅ CORRECT:
   File: "server.js", Task: "Create HTTP server"
   File: "package.json", Task: "Add express dependency"
❌ WRONG:
   File: "server.js", Task: "Create HTTP server" AND "Add express dependency"

CRITICAL RULES:
- Use "classes" array for multi-class files, set "tasks" to null
- Use "tasks" array for simple files, set "classes" to null
- NEVER use both classes and tasks at the same level
- Extract template variable names if template exists
- 🚨 CRITICAL: Each class MUST have method_signatures array (empty [] if no methods, NOT missing!)
- 🚨 If template has methods, assign EACH method to its correct class's method_signatures array
- Task IDs must be unique across entire response
- 🚨 EVERY class in template code MUST appear in classes array (don't skip any!)
- 🚨 Count classes in template carefully - if template has 6 classes, you MUST output 6 class entries

CRITICAL RESPONSE FORMAT:
- ONLY valid JSON, no markdown, no explanations
- Start with {{ and end with }}
- Must include "template_structure" field
- Task IDs unique across ALL files
- No code blocks, no comments"""



def get_helper_prompt(task_description: str, concepts: list, student_code: str,
                      question: str, previous_hints: list, help_count: int,
                      known_language: str = None, target_language: str = None, experience_level: str = "intermediate",
                      test_results: list = None) -> str:
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
    
    # Format test results if provided
    test_results_section = ""
    if test_results:
        # Correctly identify passed vs failed tests
        passed_tests = [t for t in test_results if t.get('passed') == True]
        failed_tests = [t for t in test_results if t.get('passed') == False]

        if failed_tests or passed_tests:
            test_results_section = f"\n\n{'='*60}\nTEST RESULTS:\n{'='*60}\n"
            test_results_section += f"✓ Passed: {len(passed_tests)}/{len(test_results)}\n"
            test_results_section += f"✗ Failed: {len(failed_tests)}/{len(test_results)}\n"

            if failed_tests:
                test_results_section += f"\n{'='*60}\nFAILED TEST CASES:\n{'='*60}\n"
                for i, test in enumerate(failed_tests[:3], 1):  # Show max 3 failed tests
                    test_results_section += f"\n{i}. {test.get('test_name', 'Test')}\n"
                    test_results_section += f"   Function: {test.get('function_name', 'N/A')}\n"
                    test_results_section += f"   Input: {test.get('input_data', 'N/A')}\n"
                    test_results_section += f"   Expected Output: {test.get('expected_output', 'N/A')}\n"
                    test_results_section += f"   Actual Output: {test.get('actual_output', 'N/A')}\n"
                    if test.get('error'):
                        test_results_section += f"   Error: {test.get('error')}\n"

                test_results_section += f"\n{'='*60}\n"
                test_results_section += """
CRITICAL ANALYSIS INSTRUCTIONS FOR TEST FAILURES:

🔍 STEP 1: Analyze the student's code structure and logic
   - Check if classes/methods are properly defined
   - Verify the logic matches the task requirements
   - Look for syntax errors or obvious bugs

🔍 STEP 2: Compare ACTUAL vs EXPECTED outputs
   - Look at what the code is ACTUALLY producing
   - Compare to what the test EXPECTS
   - Ask: "Is the test expectation reasonable?"

🔍 STEP 3: Determine the root cause

   IF code structure looks correct AND logic seems sound:
   ➡️ The problem is likely with TEST EXPECTATIONS, not the code
   ➡️ Tell the student: "Your code logic looks correct. The test expectations might need adjustment."
   ➡️ Point out: "Check if the expected output in the test matches what your code should produce."
   ➡️ Suggest: "Review the test's expected input/output - they may not align with your implementation."

   IF code has bugs or missing implementation:
   ➡️ Point out the specific code issue
   ➡️ Guide them to fix their implementation

   IF actual output is empty/null but code exists:
   ➡️ There's likely a compilation error, wrong method name, or runtime error
   ➡️ Check for: wrong class name, wrong method name, missing return statement

🚨 WHEN TO SUGGEST TEST CASE ADJUSTMENT:
- Student's code follows proper structure (classes, methods defined correctly)
- Logic appears sound for the task requirements
- BUT actual outputs don't match expected outputs
- This means: THE TEST EXPECTATIONS ARE PROBABLY WRONG, NOT THE CODE

Example good hint when code is correct but tests fail:
"Your MultiCellBuffer class is properly structured with the correct constructor and array initialization. The test failures suggest the test case expectations might not match your implementation. Review the test inputs and expected outputs - they may need to be adjusted to align with how your code actually works."
"""

    return f"""You are a live coding assistant helping a student who is stuck while programming.

Task Goal: {task_description}
Concepts: {concepts_str}{language_context}

Student's Current Code:
```
{student_code}
```{test_results_section}

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
                            template_variables: list = None,
                            method_signatures_by_class: dict = None) -> str:
    """
    Generate prompt for creating ONE complete file with ALL its tasks.
    Focused approach for better quality than batch generation.

    Args:
        tasks_data: List of task dicts for THIS file only
        filename: Name of file being generated
        class_structure: Dict of {class_name: [tasks]} or None for single-class
        template_variables: List of variable names to preserve from template, or None
        method_signatures_by_class: Dict of {class_name: [method_names]} for template methods
    """

    if not tasks_data:
        return ""

    # Determine language and comment style
    language = tasks_data[0].get('programming_language', 'python').lower()

    # Languages that use # for comments (Python, Shell scripts, etc.)
    if language in ['python', 'bash', 'shell', 'ruby', 'perl', 'yaml', 'toml']:
        comment_style = '#'
        comment_example = '# TODO: Implement this'
    # C/C++ and Makefile use // for code comments (even in Makefile context, the C code uses //)
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

    # Method signature preservation
    method_guidance = ""
    if method_signatures_by_class:
        method_guidance = "\n🚨 CRITICAL - TEMPLATE METHOD PRESERVATION 🚨\n\nYOU MUST CREATE THESE EXACT METHODS:\n"
        for class_name, methods in method_signatures_by_class.items():
            if methods:
                method_guidance += f"\n{class_name} class:\n"
                for method in methods:
                    method_guidance += f"  - {method}()\n"
        method_guidance += "\n ⚠️ Use EXACT names. Wrong names = autograder failure ⚠️\n"

    # Multi-class guidance (don't add examples that cause duplication)
    multi_class_example = ""

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

    requirement_extraction_guidance = """
CRITICAL - REQUIREMENT EXTRACTION FROM ASSIGNMENT:

Before generating code, carefully read the task descriptions for:

1. EXACT NAMING REQUIREMENTS:
   - Look for phrases: "MUST name", "you MUST call", "name it exactly"
   - Look for quoted names: "Producer-1", "thread-worker-01"
   - Preserve: capitalization, punctuation (dashes, underscores), numbering style
   - Example: If task says 'name threads "Producer-1"' → use "Producer-%d" with i+1

2. REQUIRED PRIMITIVES/LIBRARIES:
   - Look for: "use X", "implement using Y", "with Z library"
   - Do NOT substitute similar alternatives
   - Example: "implement with semaphores" → use semaphores (not mutex, not locks)
   - Example: "use OrderedDict" → use OrderedDict (not regular dict)

3. EXACT OUTPUT FORMATS:
   - Look for example outputs in quotes or brackets
   - Example: "[Producer-1] has produced item 5" → preserve brackets, exact wording
   - Include complete format string in TODO comments for students
   - Show example with variable names: printk(KERN_INFO "[Producer-%d] has produced...", id, ...)

4. DATA STRUCTURE IMPLICATIONS:
   - Parameters like "number of X" → create array/list to hold 0-N items
   - Example: "prod: number of producers" → need producer array, not single variable
   - Example: "size: buffer size" → need buffer of that size
   - Don't assume quantity=1 when parameter allows variable quantity

5. REQUIRED REGISTRATIONS/BOILERPLATE:
   - Look for "module must", "you must register", "required macros"
   - Include these even if TODO, so students know they're required
   - Example: kernel modules need module_init/module_exit
   - Example: Flask apps need app.run()

6. COMPLIANCE KEYWORDS:
   - "MUST", "REQUIRED", "exactly", "specifically" → follow literally
   - "may", "can", "optional" → include as TODO for flexibility
   - "do NOT", "never", "avoid" → add warning in comments

EXTRACTION PROCESS:
1. Read ALL task descriptions first
2. Extract explicit requirements (MUST, exact names, specific libraries)
3. Infer structural requirements (arrays for "number of X" parameters)
4. Include extracted requirements in relevant TODO comments
5. Don't add requirements that aren't mentioned

REQUIREMENT EXTRACTION EXAMPLES:

Example 1 - Exact Naming:
Task: "Create threads named 'Worker-1', 'Worker-2', etc."
Extraction: Must use "Worker-%d" format with 1-based indexing
Action: Include in TODO: "Name threads 'Worker-1', 'Worker-2' using format string"

Example 2 - Required Primitive:
Task: "Implement synchronization using semaphores"
Extraction: Must use semaphore library/primitives, not alternatives
Action: Declare semaphore variables, use down()/up() operations

Example 3 - Output Format:
Task: "Log messages like: [Thread-5] Processing item 42"
Extraction: Exact format with brackets, "Processing item", variable positions
Action: TODO comment shows: printk(KERN_INFO "[Thread-%d] Processing item %d", id, item)

Example 4 - Data Structure:
Task: "Parameter 'workers' specifies number of worker threads"
Extraction: Need array to hold 0-N threads, not single thread variable
Action: Declare: struct task_struct **worker_threads;

Example 5 - What NOT to extract:
Task: "Implement a producer-consumer pattern"
Extraction: No specific requirements, just the pattern
Action: Use reasonable defaults, let student make choices
"""

    return f"""Generate SCAFFOLDING CODE (starter code with TODOs) for ONE file in a programming assignment.

CRITICAL - SCAFFOLDING NOT SOLUTIONS:
⚠️  DO NOT write complete implementations
⚠️  DO NOT solve the problems for students
✓  Provide structure: class definitions, method signatures, variable declarations
✓  Use TODO comments to mark where students should write code
✓  Show the skeleton/framework, students fill in the logic

FILE: {filename}
LANGUAGE: {language}
NUMBER OF TASKS: {len(tasks_data)}

{requirement_extraction_guidance}

{structure_guidance}

{template_guidance}
{method_guidance}

Tasks for this file:
{tasks_description}

CRITICAL REQUIREMENTS:
1. Generate ONE complete, valid, compilable file: {filename}
2. {"Create all " + str(len(class_list)) + " classes with proper structure" if is_multi_class else "Use proper single-class structure"}
3. Include relevant TODOs for each task
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

REMINDER - WHAT TO INCLUDE IN code_snippet:
✓  Variable declarations (but NOT initialized with actual values students should compute)
✓  Function/method signatures (with parameter types and return types)
✓  Class structure and inheritance
✓  Import/include statements
✓  TODO comments marking where logic goes
✓  Empty method bodies or simple return statements (return 0, return null, etc.)
✗  DO NOT include actual algorithm implementations
✗  DO NOT include complete logic (loops, conditionals with actual logic)
✗  DO NOT solve the problems - leave that for students

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEFORE GENERATING - REQUIREMENT VERIFICATION CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STOP AND VERIFY YOU HAVE:
□ Read ALL task descriptions carefully for explicit requirements
□ Identified any MUST/REQUIRED/exactly keywords and followed them literally
□ Checked for quoted names or formats that must be preserved exactly
□ Identified required libraries/primitives (not substituted alternatives)
□ Created appropriate data structures for variable quantities (arrays for "number of X")
□ Included required boilerplate/registrations mentioned in tasks
□ Added requirement details to TODO comments where applicable
□ Used exact variable names from template (if template_variables provided)
□ Only added requirements that ARE mentioned (not assumed)

If assignment doesn't specify something → you have freedom to choose reasonable defaults
If assignment DOES specify something → you MUST follow it exactly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL JSON RESPONSE FORMAT - READ CAREFULLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{multi_class_example}

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