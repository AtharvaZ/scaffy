"""
Security validation utilities
"""
import re
from fastapi import HTTPException
from config import (
    MAX_ASSIGNMENT_TEXT_LENGTH,
    MAX_CODE_LENGTH,
    MAX_HINT_QUESTION_LENGTH,
    MAX_PDF_SIZE,
    MAX_TEST_CASES_PER_FILE,
    MAX_FILES_PER_ASSIGNMENT,
    MAX_TASKS_PER_ASSIGNMENT,
    BLOCKED_PATTERNS,
    ALLOWED_PDF_EXTENSIONS,
    ALLOWED_CODE_EXTENSIONS
)


def validate_text_length(text: str, max_length: int, field_name: str = "Text"):
    """Validate text input length"""
    if not text:
        raise HTTPException(status_code=400, detail=f"{field_name} cannot be empty")

    if len(text) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} exceeds maximum length of {max_length} characters (got {len(text)})"
        )

    return True


def validate_assignment_text(text: str):
    """Validate assignment text input"""
    return validate_text_length(text, MAX_ASSIGNMENT_TEXT_LENGTH, "Assignment text")


def validate_code(code: str):
    """Validate code input"""
    return validate_text_length(code, MAX_CODE_LENGTH, "Code")


def validate_hint_question(question: str):
    """Validate hint question"""
    return validate_text_length(question, MAX_HINT_QUESTION_LENGTH, "Question")


def check_malicious_content(text: str, check_type: str = "text"):
    """
    Check for potentially malicious content patterns

    Args:
        text: The text to check
        check_type: Type of content ("text", "code", etc.)

    Returns:
        True if safe, raises HTTPException if suspicious
    """
    text_lower = text.lower()

    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in text_lower:
            raise HTTPException(
                status_code=400,
                detail=f"Content contains potentially unsafe pattern: '{pattern}'. Please review your {check_type}."
            )

    return True


def validate_file_extension(filename: str, allowed_extensions: set):
    """Validate file extension"""
    import os
    ext = os.path.splitext(filename)[1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )

    return True


def validate_pdf_file(file_content: bytes, filename: str):
    """Validate PDF file upload"""
    # Check extension
    validate_file_extension(filename, ALLOWED_PDF_EXTENSIONS)

    # Check size
    if len(file_content) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"PDF file size exceeds maximum of {MAX_PDF_SIZE / (1024*1024):.1f}MB"
        )

    # Check if it's actually a PDF (magic bytes)
    if not file_content.startswith(b'%PDF'):
        raise HTTPException(
            status_code=400,
            detail="File does not appear to be a valid PDF"
        )

    return True


def validate_test_cases_count(test_cases: list):
    """Validate number of test cases"""
    if len(test_cases) > MAX_TEST_CASES_PER_FILE:
        raise HTTPException(
            status_code=400,
            detail=f"Too many test cases. Maximum allowed: {MAX_TEST_CASES_PER_FILE}"
        )
    return True


def validate_files_count(files: list):
    """Validate number of files in assignment"""
    if len(files) > MAX_FILES_PER_ASSIGNMENT:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum allowed: {MAX_FILES_PER_ASSIGNMENT}"
        )
    return True


def validate_tasks_count(tasks: list):
    """Validate number of tasks"""
    if len(tasks) > MAX_TASKS_PER_ASSIGNMENT:
        raise HTTPException(
            status_code=400,
            detail=f"Too many tasks. Maximum allowed: {MAX_TASKS_PER_ASSIGNMENT}"
        )
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks

    Removes path separators, null bytes, and other dangerous characters
    """
    # Remove path separators and null bytes
    filename = filename.replace('/', '').replace('\\', '').replace('\0', '')

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Only allow alphanumeric, dots, dashes, and underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200] + ('.' + ext if ext else '')

    return filename


def validate_language(language: str):
    """Validate programming language"""
    allowed_languages = {
        'python', 'javascript', 'typescript', 'java', 'csharp', 'c#', 'cs',
        'c++', 'cpp', 'c', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin'
    }

    if language.lower() not in allowed_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {language}. Supported: {', '.join(sorted(allowed_languages))}"
        )

    return True


def validate_request_size(content_length: int, max_size: int = MAX_PDF_SIZE):
    """Validate total request size"""
    if content_length > max_size:
        raise HTTPException(
            status_code=413,  # Payload Too Large
            detail=f"Request size exceeds maximum of {max_size / (1024*1024):.1f}MB"
        )
    return True
