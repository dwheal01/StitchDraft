from typing import List
from engine.data.models.validation_results import ValidationResult
from engine.data.models.validation_request import ValidationRequest
from engine.data.models.pattern_context import PatternContext

class PatternValidator:
    """Validates knitting patterns."""
    
    def validate_pattern(
        self,
        pattern: str,
        context: PatternContext
    ) -> ValidationResult:
        """
        Validate a knitting pattern.
        
        Args:
            pattern: The pattern string to validate
            context: Pattern context with available stitches
            
        Returns:
            ValidationResult indicating if the pattern is valid
        """
        errors = []
        
        if not pattern or not pattern.strip():
            errors.append("Pattern cannot be empty")
            return ValidationResult(is_valid=False, errors=errors)
        
        # Basic validation: check for balanced parentheses in repeat statements
        if pattern.count('(') != pattern.count(')'):
            errors.append("Unbalanced parentheses in pattern")
        
        # Validate that pattern doesn't exceed available stitches
        # This is a simplified check - actual parsing happens in PatternParser
        tokens = self._split_tokens(pattern)
        total_stitches = self._estimate_stitches(tokens, context.available_stitches)
        
        if total_stitches > context.available_stitches:
            errors.append(
                f"Pattern requires {total_stitches} stitches but only {context.available_stitches} available"
            )

        # NEW: token-level validation
        token_result = self.validate_tokens(tokens)
        if not token_result.is_valid:
            errors.extend(token_result.errors)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_tokens(self, tokens: List[str]) -> ValidationResult:
        """
        Validate pattern tokens.
        
        Args:
            tokens: List of pattern tokens
            
        Returns:
            ValidationResult indicating if tokens are valid
        """
        errors = []
        valid_operations = {'k', 'p', 'inc', 'dec', 'bo', 'yo', 'k2tog', 'ssk', 'rm', 'sm'}
        
        for token in tokens:
            # Extract operation name (before any number)
            op = ''.join(c for c in token if c.isalpha())
            if op and op not in valid_operations:
                errors.append(f"Unknown operation: {op} in token '{token}'")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def _split_tokens(self, pattern: str) -> List[str]:
        """Split pattern into tokens (simplified)."""
        # This is a simplified version - PatternParser has the full implementation
        tokens = []
        current_token = ""
        for char in pattern:
            if char in [',', ' ']:
                if current_token:
                    tokens.append(current_token.strip())
                    current_token = ""
            else:
                current_token += char
        if current_token:
            tokens.append(current_token.strip())
        return tokens
    
    def _estimate_stitches(self, tokens: List[str], available: int) -> int:
        """Estimate stitches needed (simplified - doesn't handle repeats)."""
        # This is a very simplified estimate
        # Real validation would need full pattern parsing
        return len(tokens)  # Rough estimate