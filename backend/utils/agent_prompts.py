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

CRITICAL - HANDLING LONG-RUNNING PROGRAMS:
⚠️ The test runner has a 30-second timeout limit. Programs that run longer will be terminated.

For assignments with threading, async operations, or simulations:
1. **Modify the program to run briefly** - Add early termination logic
2. **Test observable behavior quickly** - Check output within first few seconds
3. **Use time-limited tests** - Test that threads START, not that they run forever

EXAMPLES OF TIME-LIMITED TESTS:

❌ BAD (will timeout):
{{
  "test_name": "test_infinite_producer_consumer",
  "function_name": "Main",
  "expected_output": "CONTAINS:Producer,Consumer,produced 1000 items"
}}
Problem: If program runs forever or takes >30s, test will timeout

✅ GOOD (completes quickly):
{{
  "test_name": "test_producer_consumer_starts",
  "function_name": "Main",
  "expected_output": "CONTAINS:Producer started,Consumer started,produced,consumed"
}}
Solution: Test that threads START and produce SOME output, not that they complete fully

STRATEGIES FOR LONG-RUNNING PROGRAMS:

1. **Threading/Async Programs:**
   - Test that threads/tasks are created
   - Test that initial output appears
   - Don't test completion if program runs indefinitely
   - Example: "CONTAINS:Thread 1 started,Thread 2 started,Processing"

2. **Simulations/Loops:**
   - Test first few iterations only
   - Test that loop starts and produces output
   - Don't test final state if it takes >30s
   - Example: "CONTAINS:Iteration 1,Iteration 2,Iteration 3"

3. **Server/Daemon Programs:**
   - Test that server starts
   - Test initial connection/setup
   - Don't test long-running behavior
   - Example: "CONTAINS:Server started,Listening on port"

4. **Programs with Sleep/Delay:**
   - Assume student will use SHORT delays for testing
   - Test observable behavior within first 5-10 seconds
   - Example: If program sleeps 1s between iterations, test first 5 iterations

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

⚠️ TIMEOUT CONSTRAINT:
- Test runner has 30-second limit
- For programs with infinite loops or long-running threads:
  * Test INITIAL behavior (first 5-10 seconds)
  * Use CONTAINS: patterns to check for expected output
  * Don't require program completion
  * Example: Instead of "All 1000 items processed", use "CONTAINS:Processing,Item 1,Item 2"

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

Example 2b - Long-running threading program (time-limited test):
{{
  "test_name": "test_hotel_booking_threads_start",
  "function_name": "Main",
  "input_data": "",
  "expected_output": "CONTAINS:Travel Agent,Hotel,Order,room",
  "description": "Verify hotel booking system starts threads and begins processing (tests first 10 seconds only)",
  "test_type": "normal"
}}
Note: For programs that may run >30s, test INITIAL behavior only, not completion

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
    """Parser for multi-file, multi-class assignments"""

    return f"""Parse this assignment into structured tasks for a student to complete.

Assignment: {assignment_text}
Language: {target_language}
Student Level: {experience_level}

YOUR JOB:
1. Identify ALL files mentioned (code files, data files, config files, etc.)
2. For each file, create tasks that the student needs to complete
3. Break complex implementations into 20-40 minute chunks
4. Detect if template/boilerplate code is provided in the assignment

TEMPLATE DETECTION:
- Template code = starter code provided in the assignment that students must complete
- Look for code blocks, class definitions, method signatures in the assignment text
- If you find template code:
  * Set has_template: true
  * Extract exact class names: ["ClassName1", "ClassName2"]
  * Extract exact variable names that should be preserved
  * Extract method signatures at GLOBAL level (functions not in classes): ["methodName(param1, param2)"]
  * ALSO extract method signatures PER CLASS (see below)
- If NO template code is provided:
  * Set has_template: false
  * Leave arrays empty
  * Students will build from scratch

CRITICAL - METHOD SIGNATURE ASSIGNMENT:
- If template provides methods INSIDE a class, put them in that class's "method_signatures" array
- If template provides global functions (not in any class), put them in template_structure.method_signatures
- Example: If you see "class Hotel {{ void UpdatePrice() {{...}} }}", put "UpdatePrice()" in Hotel's method_signatures
- This helps preserve the exact structure students need to complete

TASK BREAKDOWN STRATEGY:
- Code files: Break into logical implementation tasks (setup, core logic, error handling, etc.)
- Data files: Create tasks for populating them (e.g., "Create Hotels.xml with sample hotel data")
- Config files: Create tasks for configuration (e.g., "Set up database connection in config.json")
- Multi-class files: Group tasks by class using the classes array
- Simple files: Use flat tasks array

OUTPUT STRUCTURE:
{{
  "overview": "Brief 2-sentence summary of assignment",
  "total_estimated_time": "X hours Y minutes",
  "template_structure": {{
    "has_template": true/false,
    "variable_names": ["exact_names_from_template"],
    "class_names": ["ClassName1", "ClassName2"],
    "method_signatures": ["method1()", "method2()"]
  }},
  "files": [
    // MULTI-CLASS FILE (multiple classes in one file)
    {{
      "filename": "example.cs",
      "purpose": "Brief description",
      "classes": [
        {{
          "class_name": "ClassName",
          "purpose": "What this class does",
          "method_signatures": ["method1()", "method2()"],
          "tasks": [
            {{"id": 1, "title": "...", "description": "...", "dependencies": [], "estimated_time": "30 min", "concepts": ["..."]}}
          ]
        }}
      ],
      "tasks": null
    }},
    // SIMPLE FILE (single class or no classes)
    {{
      "filename": "utils.py",
      "purpose": "Brief description",
      "classes": null,
      "tasks": [
        {{"id": 2, "title": "...", "description": "...", "dependencies": [1], "estimated_time": "20 min", "concepts": ["..."]}}
      ]
    }}
  ]
}}

KEY RULES:
1. EVERY file needs tasks - code files AND data files AND config files
2. Multi-class files: use "classes" array (set "tasks" to null)
3. Simple files: use "tasks" array (set "classes" to null)
4. NEVER have both "classes" and "tasks" in the same file
5. Dependencies are INTEGERS (task IDs), not strings: [1, 2] not ["Task 1"]
6. Include ALL files mentioned in assignment (don't skip data/config files)
7. CRITICAL: Assign method_signatures to the CLASS they belong to, NOT globally

EXAMPLE - Correct Method Signature Assignment:
If template provides:
```
class Hotel {{
  void UpdatePrice() {{ }}
  void ProcessOrder() {{ }}
}}
class TravelAgent {{
  void CreateOrder() {{ }}
}}
```

Correct output:
{{
  "template_structure": {{
    "has_template": true,
    "class_names": ["Hotel", "TravelAgent"],
    "method_signatures": []  // Empty - all methods belong to classes
  }},
  "files": [{{
    "classes": [
      {{
        "class_name": "Hotel",
        "method_signatures": ["UpdatePrice()", "ProcessOrder()"]  // Hotel's methods HERE
      }},
      {{
        "class_name": "TravelAgent",
        "method_signatures": ["CreateOrder()"]  // TravelAgent's methods HERE
      }}
    ]
  }}]
}}

Return ONLY valid JSON."""

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


def get_non_code_file_prompt(tasks_data: list, filename: str) -> str:
    """
    Generate prompt for non-code files (data, config, build files, etc.)
    These should contain actual content, not code to generate them
    """
    if not tasks_data:
        return ""

    # Get file extension and base name to determine format
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    basename = filename.lower()

    # Build task descriptions
    tasks_description = ""
    for i, task in enumerate(tasks_data, 1):
        tasks_description += f"\nTask {i}: {task['task_description']}"

    # Detect file type and provide specific guidance
    if basename == 'makefile' or basename.startswith('makefile'):
        file_type = "Makefile"
        guidance = "Generate a valid Makefile with targets, dependencies, and build commands using tab indentation"
    elif basename in ['dockerfile', 'dockerfile.dev', 'dockerfile.prod']:
        file_type = "Dockerfile"
        guidance = "Generate a valid Dockerfile with FROM, RUN, COPY, CMD instructions"
    elif basename == 'cmakelists.txt':
        file_type = "CMakeLists.txt"
        guidance = "Generate a valid CMake configuration with project(), add_executable(), etc."
    elif ext in ['xml', 'xsd']:
        file_type = ext.upper()
        guidance = "Generate valid XML/XSD with proper structure, elements, and attributes"
    elif ext in ['json', 'yaml', 'yml', 'toml']:
        file_type = ext.upper()
        guidance = f"Generate valid {ext.upper()} with proper structure and data types"
    elif ext in ['sh', 'bat', 'ps1']:
        file_type = "Shell Script"
        guidance = f"Generate a valid {ext} script with proper syntax and commands"
    elif ext in ['properties', 'ini', 'cfg', 'env']:
        file_type = "Config File"
        guidance = f"Generate a valid {ext} config file with key-value pairs"
    elif basename.endswith('ignore'):
        file_type = "Ignore File"
        guidance = f"Generate a {filename} file with appropriate glob patterns"
    else:
        file_type = ext.upper() if ext else "file"
        guidance = "Generate appropriate content for this file format"

    return f"""Generate MINIMAL starter content for {file_type}: {filename}

TASKS:{tasks_description}

IMPORTANT - KEEP IT SHORT:
- Generate only 2-3 sample entries (NOT 10+)
- Keep total content under 50 lines
- Students will expand this file themselves
- Focus on demonstrating structure, not filling with data

CRITICAL INSTRUCTIONS:
1. Generate the ACTUAL {file_type} content - NOT code to create it
2. This is NOT a source code file - it's a {file_type.lower()}
3. {guidance}
4. Include helpful comments where appropriate
5. Create realistic, functional content that demonstrates proper structure
6. For Makefiles: Use TABS (\\t) for indentation, not spaces
7. Make it ready to use with minimal modifications

JSON OUTPUT FORMAT (CRITICAL):
- NO markdown code blocks (no ```)
- Escape ALL newlines as \\n
- Escape ALL tabs as \\t
- Escape ALL quotes as \\"
- The entire file content must be on ONE LINE in the JSON string

CORRECT EXAMPLE:
{{
  "code_snippet": "<?xml version=\\"1.0\\"?>\\n<hotels>\\n  <hotel>\\n    <name>Grand Hotel</name>\\n  </hotel>\\n</hotels>",
  "task_todos": {{
    "1": ["Review and customize as needed", "Test functionality"]
  }}
}}

WRONG (will fail):
{{
  "code_snippet": "<?xml version=\\"1.0\\"?>
<hotels>
  <hotel>
"""


def get_file_codegen_prompt(tasks_data: list, filename: str,
                            class_structure: dict = None,
                            template_variables: list = None,
                            method_signatures_by_class: dict = None) -> str:
    """
    Generate scaffolding for ONE complete file with proper TODOs based on experience level.
    """
    if not tasks_data:
        return ""

    # Language detection and comment style
    language = tasks_data[0].get('programming_language', 'python').lower()
    comment_style = '#' if language in ['python', 'bash', 'shell', 'ruby', 'perl', 'yaml', 'toml'] else '//'
    
    # Structure detection
    is_multi_class = class_structure and len(class_structure) > 1
    class_list = sorted(class_structure.keys()) if class_structure else []
    
    # Build task descriptions (CRITICAL - must include what to implement!)
    tasks_description = ""
    for i, task in enumerate(tasks_data, 1):
        tasks_description += f"""
Task {i}: {task['task_description']}
  Class: {task.get('class_name', 'Program')}
  Concepts: {', '.join(task.get('concepts', []))}
  Experience: {task.get('experience_level', 'intermediate')}
  
  WHAT TO IMPLEMENT:
  - Read the task description carefully
  - Create method(s) that accomplish this specific task
  - Add TODOs inside the method body based on experience level
  - Ensure the method signature matches what the task requires"""
        if task.get('template_variables'):
            tasks_description += f"\n  Preserve variables: {', '.join(task['template_variables'])}"

    # Template preservation section (if needed)
    template_section = ""
    if template_variables or method_signatures_by_class:
        template_section = "\nTEMPLATE REQUIREMENTS:"
        if template_variables:
            template_section += f"\n- Preserve exact variable names: {', '.join(template_variables)}"
        if method_signatures_by_class:
            template_section += "\n- Create these exact methods:"
            for cls, methods in method_signatures_by_class.items():
                template_section += f"\n  {cls}: {', '.join(methods)}"

    # Class structure section (if multi-class)
    structure_section = ""
    if is_multi_class:
        structure_section = f"\nFILE STRUCTURE: Create {len(class_list)} classes: {', '.join(class_list)}"
        for cls in class_list:
            task_count = len([t for t in tasks_data if t.get('class_name') == cls])
            structure_section += f"\n- {cls}: {task_count} tasks"

    # Language-specific requirements
    lang_requirements = {
        'csharp': "Use ONE namespace containing all classes. Include: using System; etc.",
        'c#': "Use ONE namespace containing all classes. Include: using System; etc.",
        'java': "Use ONE package. Include proper imports. Main class must be public.",
        'c': "Include headers: #include <stdio.h>, etc. Use proper function prototypes.",
        'c++': "Include headers. Use namespace std or explicit std:: prefixes.",
        'python': "Include imports at top. Use proper indentation (4 spaces).",
        'javascript': "Use modern ES6+ syntax. Include 'use strict' if needed.",
        'typescript': "Include type annotations. Define interfaces where appropriate."
    }
    
    lang_specific = lang_requirements.get(language, "")

    return f"""Generate scaffolding code for: {filename}

CRITICAL INSTRUCTIONS:
- You are creating STARTER CODE for students to complete
- Generate syntactically valid code with EMPTY method bodies
- Place TODOs inside methods to guide students
- Do NOT implement the full logic - students will do that
- Focus on creating the right structure and clear guidance

ASSIGNMENT TASKS:{tasks_description}
{structure_section}
{template_section}

REQUIREMENTS:
1. Language: {language}
2. Comment style: {comment_style} for all TODOs
3. Generate ONE complete file with SCAFFOLDING CODE - each class appears EXACTLY ONCE
4. Include method signatures with EMPTY bodies containing TODOs (NOT full implementations)
5. The code should be SYNTACTICALLY VALID but NOT functionally complete
6. {lang_specific}

CRITICAL - AVOID DUPLICATION:
- Each class declaration must appear EXACTLY ONCE in code_snippet
- Do NOT repeat class declarations in comments or examples
- If the file has "class Program", it should appear exactly 1 time in the entire code

TODO GUIDELINES BY EXPERIENCE (CRITICAL - Follow exactly):

BEGINNER (5-8 TODOs per task):
- Break down EVERY step of the implementation
- Include TODOs for variable declarations, loops, conditionals, return statements
- Use simple, instructional language
- Example for "validate input" task:
  {comment_style} TODO: Check if input is null or empty
  {comment_style} TODO: Check if input length is within valid range (1-100)
  {comment_style} TODO: Check if input contains only allowed characters
  {comment_style} TODO: If any validation fails, return false
  {comment_style} TODO: If all validations pass, return true

INTERMEDIATE (3-5 TODOs per task):
- Group related steps into logical sections
- Assume basic programming knowledge
- Focus on the main logic blocks
- Example for "validate input" task:
  {comment_style} TODO: Validate input is not null/empty and within length limits
  {comment_style} TODO: Check input contains only allowed characters
  {comment_style} TODO: Return validation result

ADVANCED (1-3 TODOs per task):
- High-level implementation goals only
- Assume strong programming skills
- Minimal guidance
- Example for "validate input" task:
  {comment_style} TODO: Implement input validation logic
  {comment_style} TODO: Return validation result

PLACEMENT RULES:
- Place TODOs INSIDE method bodies where code should be written
- Do NOT put TODOs in class declarations or import statements
- Each TODO should describe ONE specific action to take
- TODOs should be ordered in the sequence they need to be implemented

SPECIAL HANDLING:

Threading/Async ({language}):
- Include thread creation structure
- Add synchronization primitives (mutex/semaphore/lock)
- TODO for thread safety considerations

File I/O:
- Include file handling structure (open/close)
- Add error handling scaffolding
- TODO for exception handling

Networking:
- Include connection setup/teardown
- Add protocol handling structure
- TODO for error recovery

Data Structures:
- Initialize with proper type declarations
- Include size/capacity management
- TODO for boundary checking

JSON OUTPUT (NO ```):
{{
  "code_snippet": "complete file code here with \\n for newlines",
  "task_todos": {{
    "1": ["todo for task 1", "another todo for task 1"],
    "2": ["todo for task 2", "another todo for task 2"],
    "3": ["todo for task 3"]
  }}
}}

EXAMPLE OUTPUT (Python, Beginner level, 2 tasks):
{{
  "code_snippet": "# File: string_utils.py\\n\\ndef reverse_string(text):\\n    # TODO: Check if text is None or empty\\n    # TODO: Create an empty result variable\\n    # TODO: Loop through text from end to start\\n    # TODO: Add each character to result\\n    # TODO: Return the result\\n    pass\\n\\ndef count_vowels(text):\\n    # TODO: Create a variable to count vowels\\n    # TODO: Define which characters are vowels\\n    # TODO: Loop through each character in text\\n    # TODO: Check if character is a vowel\\n    # TODO: If yes, increment the counter\\n    # TODO: Return the counter\\n    pass",
  "task_todos": {{
    "1": ["Check if text is None or empty", "Create an empty result variable", "Loop through text from end to start", "Add each character to result", "Return the result"],
    "2": ["Create a variable to count vowels", "Define which characters are vowels", "Loop through each character in text", "Check if character is a vowel", "If yes, increment the counter", "Return the counter"]
  }}
}}"""