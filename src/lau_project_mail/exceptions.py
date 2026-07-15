class MailError(Exception):
    """Base exception for all Mail-related errors."""
    pass


class MissingFieldError(MailError):
    """Raised when a required field is missing before an operation."""
    pass


class GenerationError(MailError):
    """Raised when the LLM fails to generate a valid mail."""
    pass


class SendError(MailError):
    """Raised when sending the email fails."""
    pass