import re
from typing import List
from engine.data.models.validation_results import ValidationResult
from engine.data.models.validation_request import ValidationRequest
from engine.data.models.pattern_context import PatternContext

# Must match PatternParser.CONSUME_PRODUCE only. Do not add yo, k2tog, ssk (not in parser).
VALID_PATTERN_OPERATIONS = frozenset({
    'k', 'p', 'inc', 'dec', 'pm', 'bo', 'rm', 'co', 'sm', 'workest', 'contasest',
})

ALLOWED_OPS_HINT = "Allowed: k, p, inc, dec, bo, co, pm, rm, sm, work est, cont as est, repeat(...)."


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
        
        # Normalize "work est", "cont as est", etc. to single tokens so _split_tokens doesn't break them
        pattern = self._normalize_work_est_in_pattern(pattern)
        # Validate that pattern doesn't exceed available stitches
        # This is a simplified check - actual parsing happens in PatternParser
        tokens = self._split_tokens(pattern)
        total_stitches = self._estimate_stitches(tokens, context.available_stitches)
        
        if total_stitches > context.available_stitches:
            errors.append(
                f"Pattern requires {total_stitches} stitches but only {context.available_stitches} available"
            )

        # Token-level validation
        token_result = self.validate_tokens(tokens)
        if not token_result.is_valid:
            errors.extend(token_result.errors)
            errors.append(ALLOWED_OPS_HINT)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_tokens(self, tokens: List[str]) -> ValidationResult:
        """
        Validate pattern tokens. Skips repeat(...) tokens; validates inner ops if desired.
        """
        errors = []
        for token in tokens:
            # Skip repeat(...) as a whole; optionally validate inner part (case-insensitive)
            t = token.strip()
            if t.lower().startswith('repeat(') and t.endswith(')'):
                inner = t[7:-1]  # "repeat(" -> 7 chars, ")" -> 1
                inner_tokens = self._split_tokens(inner)
                inner_result = self._validate_tokens_inner(inner_tokens)
                if not inner_result.is_valid:
                    errors.extend(inner_result.errors)
                continue
            op = ''.join(c for c in token if c.isalpha()).lower()
            if op and op not in VALID_PATTERN_OPERATIONS:
                errors.append(f"Unknown operation: {op} in token '{token}'")
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def _validate_tokens_inner(self, tokens: List[str]) -> ValidationResult:
        """Validate a list of tokens (e.g. inside repeat(...)). Case-insensitive."""
        errors = []
        for token in tokens:
            op = ''.join(c for c in token if c.isalpha()).lower()
            if op and op not in VALID_PATTERN_OPERATIONS:
                errors.append(f"Unknown operation: {op} in token '{token}'")
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def _normalize_work_est_in_pattern(self, pattern: str) -> str:
        """Replace 'work est', 'cont as est', etc. with single-word forms so tokenization keeps them as one token.
        Without this, space splitting would turn 'work est' into 'work' + 'est' and 'cont as est' into 'cont' + 'as' + 'est', all invalid."""
        # Longer phrases first; use word boundaries so we don't match inside other words
        pattern = re.sub(r'\bwork\s+established\b', 'workest', pattern, flags=re.IGNORECASE)
        pattern = re.sub(r'\bwork\s+est\b', 'workest', pattern, flags=re.IGNORECASE)
        pattern = re.sub(r'\bcont\s+as\s+established\b', 'contasest', pattern, flags=re.IGNORECASE)
        pattern = re.sub(r'\bcont\s+as\s+est\b', 'contasest', pattern, flags=re.IGNORECASE)
        pattern = re.sub(r'\best\b', 'workest', pattern, flags=re.IGNORECASE)
        return pattern

    def _split_tokens(self, pattern: str) -> List[str]:
        """Split pattern into tokens; do not split on comma inside parentheses (e.g. repeat(k5, p5))."""
        tokens = []
        current_token = ""
        depth = 0
        for char in pattern:
            if char == '(':
                depth += 1
                current_token += char
            elif char == ')':
                depth -= 1
                current_token += char
            elif char in [',', ' '] and depth == 0:
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