import re
from typing import List
from engine.data.models.validation_results import ValidationResult
from engine.data.models.validation_request import ValidationRequest
from engine.data.models.pattern_context import PatternContext
from engine.domain.models.marker_manager import MarkerManager
from engine.domain.models.pattern_parser import PatternParser

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
        
        # Allow empty/whitespace patterns as a "work nothing" row/segment.
        # This is useful for leaving stitches unconsumed on the needle.
        if not pattern or not pattern.strip():
            return ValidationResult(is_valid=True, errors=[])
        
        # Basic validation: check for balanced parentheses in repeat statements
        if pattern.count('(') != pattern.count(')'):
            errors.append("Unbalanced parentheses in pattern")
        
        # Normalize "work est", "cont as est", etc. to single tokens so _split_tokens doesn't break them
        pattern = self._normalize_work_est_in_pattern(pattern)
        tokens = self._split_tokens(pattern)

        # Validate stitch consumption using the real PatternParser logic (including repeat(...)).
        # This keeps validation consistent with execution.
        try:
            self._estimate_stitches(pattern, context)
        except ValueError as e:
            errors.append(str(e))

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
    
    def _estimate_stitches(self, pattern: str, context: PatternContext) -> int:
        """
        Estimate stitches consumed using PatternParser.

        Note: the parser returns the number of stitches consumed from the current needle segment(s).
        It may be less than available (e.g. bind-offs) but will raise if consumption exceeds availability.
        """
        marker_manager = MarkerManager()
        for m in (getattr(context, "markers", None) or []):
            try:
                marker_manager.add_marker(context.side, int(m), context.available_stitches)
            except Exception:
                # If a marker is malformed, let the parser/other validation handle it later.
                continue

        parser = PatternParser(marker_provider=marker_manager)
        last_row = getattr(context, "last_row", None)
        is_round = getattr(context, "is_round", False)
        expanded = parser.expand_pattern(
            pattern=pattern,
            available_stitches=context.available_stitches,
            side=context.side,
            last_row=last_row,
            is_round=is_round,
        )
        return expanded.consumed