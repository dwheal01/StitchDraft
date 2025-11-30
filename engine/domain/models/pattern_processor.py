from typing import List, TYPE_CHECKING
from engine.domain.models.pattern_parser import PatternParser
from engine.domain.models.validators.pattern_validator import PatternValidator
from engine.data.models.pattern_context import PatternContext
from engine.data.models.expanded_pattern import ExpandedPattern
from engine.data.models.validation_results import ValidationResult

if TYPE_CHECKING:
    from engine.domain.interfaces.imarker_provider import IMarkerProvider


class PatternProcessor:
    """
    Wrapper around PatternParser that provides a higher-level interface
    for pattern processing with validation.
    """
    
    def __init__(
        self,
        pattern_parser: PatternParser = None,
        pattern_validator: PatternValidator = None
    ):
        """
        Initialize PatternProcessor.
        
        Args:
            pattern_parser: PatternParser instance (will create one if None)
            pattern_validator: PatternValidator instance (will create one if None)
        """
        self.pattern_parser = pattern_parser
        self.pattern_validator = pattern_validator or PatternValidator()
    
    def expand_pattern(
        self,
        pattern: str,
        context: PatternContext
    ) -> ExpandedPattern:
        """
        Expand a pattern string using PatternParser.
        
        Args:
            pattern: Pattern string to expand
            context: PatternContext with available stitches, side, markers, etc.
            
        Returns:
            ExpandedPattern result
        """
        expanded = self.pattern_parser.expand_pattern(
            pattern,
            context.available_stitches,
            context.side
        )
        # expanded is already an ExpandedPattern, just return it
        return expanded
    
    def validate_pattern(
        self,
        pattern: str,
        context: PatternContext
    ) -> bool:
        """
        Validate a pattern without expanding it.
        
        Args:
            pattern: The pattern string to validate
            context: PatternContext with available stitches, side, etc.
            
        Returns:
            True if pattern is valid, False otherwise
        """
        result = self.pattern_validator.validate_pattern(pattern, context)
        return result.is_valid
    
    def process_markers(
        self,
        pattern: str,
        context: PatternContext
    ) -> List[int]:
        """
        Process markers in a pattern and return marker positions.
        This is a convenience method that expands the pattern and extracts markers.
        
        Args:
            pattern: The pattern string to process
            context: PatternContext with available stitches, side, etc.
            
        Returns:
            List of marker positions
        """
        expanded_pattern = self.expand_pattern(pattern, context)
        return expanded_pattern.markers
    
    def validate_and_expand(
        self,
        pattern: str,
        context: PatternContext
    ) -> ExpandedPattern:
        """
        Validate a pattern and then expand it if valid.
        
        Args:
            pattern: The pattern string to validate and expand
            context: PatternContext with available stitches, side, etc.
            
        Returns:
            ExpandedPattern if valid
            
        Raises:
            ValueError: If pattern validation fails
        """
        # Validate first
        validation_result = self.pattern_validator.validate_pattern(pattern, context)
        
        if not validation_result.is_valid:
            error_message = "; ".join(validation_result.errors)
            raise ValueError(f"Pattern validation failed: {error_message}")
        
        # If valid, expand
        return self.expand_pattern(pattern, context)