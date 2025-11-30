"""
Security and configuration settings for the Scaffy backend
"""

# ============================================
# SIZE LIMITS
# ============================================

# Text input limits (in characters)
MAX_ASSIGNMENT_TEXT_LENGTH = 50_000  # ~50KB of text (about 10,000 words)
MAX_CODE_LENGTH = 100_000  # ~100KB (reasonable for most assignments)
MAX_HINT_QUESTION_LENGTH = 3_000  # For hint questions

# File upload limits (in bytes)
MAX_PDF_SIZE = 7 * 1024 * 1024  # 7MB for PDFs
MAX_TOTAL_FILES_SIZE = 20 * 1024 * 1024  # 20MB total for all files in a request

# Number limits
MAX_TEST_CASES_PER_FILE = 20  # Maximum test cases per file
MAX_FILES_PER_ASSIGNMENT = 10  # Maximum files in a multi-file assignment
MAX_TASKS_PER_ASSIGNMENT = 30  # Maximum tasks to prevent abuse

# ============================================
# RATE LIMITING
# ============================================

RATE_LIMIT_PER_MINUTE = 30  # Max requests per minute per IP
RATE_LIMIT_PER_HOUR = 300  # Max requests per hour per IP
RATE_LIMIT_PER_DAY = 1000  # Daily cap to prevent abuse

# ============================================
# CONTENT VALIDATION
# ============================================

# Allowed file extensions for uploads
ALLOWED_PDF_EXTENSIONS = {'.pdf'}
ALLOWED_CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs',
    '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
    '.sh', '.txt', '.md', '.json', '.xml', '.yaml', '.yml'
}

# Blocked patterns (for security)
BLOCKED_PATTERNS = [
    # System commands
    'rm -rf', 'format c:', 'del /f', 'DROP TABLE', 'DROP DATABASE',
    # Malicious code patterns
    'eval(', 'exec(', '__import__', 'os.system', 'subprocess.call',
    # Crypto mining
    'cryptonight', 'coinhive', 'crypto-loot',
]

# ============================================
# API KEYS & SECRETS
# ============================================

# These should be in environment variables, not hardcoded
REQUIRED_ENV_VARS = [
    'ANTHROPIC_API_KEY',
]

# ============================================
# TIMEOUT SETTINGS
# ============================================

API_TIMEOUT_SECONDS = 60  # Max time for API calls
CODE_EXECUTION_TIMEOUT = 30  # Max time for code execution (Piston)
PDF_PROCESSING_TIMEOUT = 30  # Max time for PDF processing

# ============================================
# LOGGING
# ============================================

LOG_SENSITIVE_DATA = False  # Never log API keys or user code in production
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
