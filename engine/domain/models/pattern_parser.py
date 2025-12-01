from typing import Dict, Tuple, List
from engine.domain.interfaces.imarker_provider import IMarkerProvider
from engine.data.models.expanded_pattern import ExpandedPattern

class PatternParser:
    """Handles parsing and expansion of knitting patterns."""
    
    CONSUME_PRODUCE: Dict[str, Tuple[int, int]] = {
        "k": (1, 1),
        "p": (1, 1),
        "inc": (0, 1),
        "dec": (2, 1),
        "pm": (0, 0), #place marker
        "bo": (1, 0), # bind off
        "rm": (0, 0), # remove marker
        "co": (0, 1), # cast on
        "sm": (0, 0) # slip marker
    }
    
    def __init__(self, marker_provider: IMarkerProvider):
        """
        Initialize PatternParser with a marker provider.
        
        Args:
            marker_provider: An object implementing IMarkerProvider interface
        """
        self.marker_provider = marker_provider
    
    def expand_pattern(self, pattern: str, available_stitches: int, side: str) -> ExpandedPattern:
        """Expand a pattern string into stitches."""
        markers = []
        expanded = []
        consumed = 0
        produced = 0
        last_row_len = available_stitches
        leading_sts = 0
        bind_off_count = 0
        
        # Split pattern into segments separated by 'sm'
        segments, noted_markers, markers_for_removal = self._split_by_sm(pattern, side)
        noted_markers.append(last_row_len)
        for i, segment in enumerate(segments):
            num_increases = 0
            num_decreases = 0
            repeat_idx = -1
            tokens = self.split_tokens(segment)
            for j,token in enumerate(tokens):
                  if token.startswith("repeat(") and token.endswith(")"):
                     # if there is already a repeat in this segement throw an error
                     if repeat_idx != -1:
                        raise ValueError(f"Repeat found in segment {i} ('{segment}') more than once")
                     repeat_idx = j
                     leading_sts = produced + bind_off_count
                  else:
                     s, count = self.parse_token(token)
                     if s == "inc":
                        num_increases += count
                     elif s == "dec":
                        num_decreases += count
                     if s == "pm":
                        for _ in range(max(count, 1)):
                              markers.append(produced)
                        continue
                     for _ in range(count):
                        cons, prod = self.CONSUME_PRODUCE.get(s, (1, 1))
                        if consumed + cons > noted_markers[i]:
                              raise ValueError(
                                 f"Row would consume {consumed + cons} but only {noted_markers[i]} available"
                              )
                        consumed += cons
                        produced += prod
                        if s == "bo":
                            bind_off_count += 1
                        expanded.append(s)
            if repeat_idx != -1:
               token = tokens[repeat_idx]
               inner = token[len("repeat("):-1].strip()
               inner_tokens = self.split_tokens(inner)
               for _ in range(noted_markers[i] - consumed):
                  for inner_token in inner_tokens:
                     s, count = self.parse_token(inner_token)
                     if s == "inc":
                        num_increases += count
                     elif s == "dec":
                        num_decreases += count
                     if s == "pm":
                        # pm does not consume or produce; store position count times
                        for _ in range(max(count, 1)):
                           markers.append(produced)
                        continue
                     for _ in range(count):
                        cons, prod = self.CONSUME_PRODUCE.get(s, (1, 1))
                        if consumed + cons > noted_markers[i]:
                           break
                        consumed += cons
                        produced += prod
                        expanded.insert(leading_sts, s)
                        leading_sts += 1
                     if consumed >= noted_markers[i]:
                        break
            # Validate that this segment consumed exactly the expected number of stitches
            # if consumed != noted_markers[i]:
            #     raise ValueError(
            #         f"Segment {i} ('{segment}') consumed {consumed} stitches but expected {noted_markers[i]} stitches"
            #     )
            if noted_markers[i] not in markers_for_removal:
                self.marker_provider.move_marker(side, i, num_increases - num_decreases, produced + (last_row_len - consumed))
            else:
                self.marker_provider.remove_marker(side, noted_markers[i])
        
        return ExpandedPattern(
            stitches=expanded,
            consumed=consumed,
            produced=produced,
            markers=markers
        )
 
    def _split_by_sm(self, pattern: str, side: str) -> Tuple[List[str], List[int], List[int]]:
        """Split pattern by 'sm' tokens, preserving the sm tokens."""
        tokens = self.split_tokens(pattern)
        segments = []
        current_segment = []
        noted_markers = []
        markers_for_removal = []

        marker_index = 0
        markers_list = self.marker_provider.get_markers(side)
        for token in tokens:
            if token == "sm" or token == "rm":
                # if token == "rm":
                #     print("removing marker at index: ", marker_index)
                #     self.marker_provider.remove_marker(side, marker_index)
                if current_segment:
                    segments.append(",".join(current_segment))
                    current_segment = []
                if marker_index >= len(markers_list):
                    raise ValueError(f"More markers than markers in {side}")
                noted_markers.append(markers_list[marker_index])
                if token == "rm":
                    markers_for_removal.append(markers_list[marker_index])
                marker_index += 1
            else:
                current_segment.append(token)
        
        if current_segment:
            segments.append(",".join(current_segment))
        
        return segments, noted_markers, markers_for_removal
     
    def split_tokens(self, pattern: str) -> List[str]:
        """Split pattern into tokens, handling parentheses."""
        tokens, buf, depth = [], "", 0
        for ch in pattern:
            if ch == "," and depth == 0:
                if buf.strip():
                    tokens.append(buf.strip())
                buf = ""
            else:
                buf += ch
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
        if buf.strip():
            tokens.append(buf.strip())
        return tokens
    
    @staticmethod
    def parse_token(token: str) -> Tuple[str, int]:
        """Parse token like 'k2' into ('k', 2)."""
        stitch = ''.join([c for c in token if not c.isdigit()])
        digits = ''.join([c for c in token if c.isdigit()])
        count = int(digits) if digits else 1
        if stitch in ("inc", "dec") and count == 0:
           count = 1
        return stitch, count