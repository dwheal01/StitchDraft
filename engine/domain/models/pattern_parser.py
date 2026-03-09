from typing import Dict, Tuple, List, Optional
from engine.domain.interfaces.imarker_provider import IMarkerProvider
from engine.data.models.expanded_pattern import ExpandedPattern

# Tokens that mean "work as established" (continue previous row's k/p)
WORK_EST_ALIASES = ("work est", "work established", "est", "cont as est", "cont as established")


class PatternParser:
    """Handles parsing and expansion of knitting patterns."""
    
    CONSUME_PRODUCE: Dict[str, Tuple[int, int]] = {
        "k": (1, 1),
        "p": (1, 1),
        "inc": (0, 1),
        "dec": (2, 1),
        "pm": (0, 0),  # place marker
        "bo": (1, 0),  # bind off
        "rm": (0, 0),  # remove marker
        "co": (0, 1),  # cast on
        "sm": (0, 0),  # slip marker
        "work_est": (1, 1),
    }
    
    def __init__(self, marker_provider: IMarkerProvider):
        """
        Initialize PatternParser with a marker provider.
        
        Args:
            marker_provider: An object implementing IMarkerProvider interface
        """
        self.marker_provider = marker_provider
    
    def _normalize_work_est(self, stitch: str) -> str:
        """Map 'work est', 'work established', 'est' to 'work_est'."""
        # Collapse all whitespace to single space so "work  est" and unicode spaces match
        normalized = " ".join(stitch.strip().lower().split())
        return "work_est" if normalized in WORK_EST_ALIASES else stitch
    
    def _consumption_of_tokens(self, tokens: List[str], start_idx: int) -> int:
        """Total stitches consumed by tokens from start_idx to end (for fill-segment work_est)."""
        total = 0
        for idx in range(start_idx, len(tokens)):
            token = tokens[idx]
            if token.startswith("repeat(") and token.endswith(")"):
                continue
            s, count = self.parse_token(token)
            s = self._normalize_work_est(s)
            if s == "pm":
                continue
            cons, _ = self.CONSUME_PRODUCE.get(s, (1, 1))
            total += cons * count
        return total

    def _consumption_of_inner(self, inner_tokens: List[str]) -> int:
        """Stitches consumed by one repetition of the inner pattern (e.g. repeat(k2) -> 2)."""
        total = 0
        for token in inner_tokens:
            s, count = self.parse_token(token)
            s = self._normalize_work_est(s)
            if s == "pm":
                continue
            cons, _ = self.CONSUME_PRODUCE.get(s, (1, 1))
            total += cons * count
        return total
    
    def _work_est_stitch(self, prev_stitch: str, side: str, is_round: bool) -> str:
        """Return stitch for 'work as established': match how the fabric looks on the RS.
        Previous row was worked on the opposite side (RS if we're on WS, WS if we're on RS).
        - Previous row on RS: what we did (k/p) is what shows on RS.
        - Previous row on WS: what we did shows as the opposite on RS (purl→knit, knit→purl).
        So we compute previous_rs_appearance, then work the stitch that reproduces it this row.
        """
        if is_round:
            return prev_stitch  # in the round, always same as previous
        # Previous row's side is opposite of current
        prev_was_rs = side == "WS"
        prev_rs_appearance = prev_stitch if prev_was_rs else ("p" if prev_stitch == "k" else "k")
        if prev_stitch not in ("k", "p"):
            return prev_stitch  # inc, dec, bo, etc. unchanged
        # This row: work the stitch that shows as prev_rs_appearance on the RS
        if side == "RS":
            return prev_rs_appearance  # knit to show knit, purl to show purl
        return "p" if prev_rs_appearance == "k" else "k"  # WS: purl to show knit, knit to show purl
    
    def expand_pattern(
        self,
        pattern: str,
        available_stitches: int,
        side: str,
        last_row: Optional[List[str]] = None,
        is_round: bool = False,
    ) -> ExpandedPattern:
        """Expand a pattern string into stitches."""
        markers = []
        expanded = []
        consumed = 0
        produced = 0
        warnings: List[str] = []
        last_row_len = available_stitches
        leading_sts = 0
        bind_off_count = 0
        
        # Split pattern into segments separated by 'sm'
        segments, noted_markers, markers_for_removal = self._split_by_sm(pattern, side)
        noted_markers.append(last_row_len)
        for i, segment in enumerate(segments):
            num_increases = 0
            num_decreases = 0
            segment_start_consumed = consumed
            tokens = self.split_tokens(segment)
            # Alignment warning (MVP): pure repeat(...) row where repeat width doesn't divide segment stitch count.
            # Example: 11 sts with repeat(k1,p1) -> partial repeat (unwinds visually).
            if len(tokens) == 1 and tokens[0].startswith("repeat(") and tokens[0].endswith(")"):
                inner = tokens[0][len("repeat("):-1].strip()
                inner_tokens = self.split_tokens(inner)
                normalized_inner = []
                for t in inner_tokens:
                    s, _ = self.parse_token(t)
                    normalized_inner.append(self._normalize_work_est(s))
                if not any(s in ("inc", "dec", "bo", "co") for s in normalized_inner):
                    inner_width = self._consumption_of_inner(inner_tokens)
                    segment_available = max(0, noted_markers[i] - segment_start_consumed)
                    if inner_width > 0 and segment_available % inner_width != 0:
                        warnings.append(
                            f"Pattern '{tokens[0]}' repeats every {inner_width} stitch(es) but "
                            f"{segment_available} stitch(es) are available; final repeat will be partial "
                            f"and the pattern may not align."
                        )
            repeat_indices = [j for j, t in enumerate(tokens) if t.startswith("repeat(") and t.endswith(")")]
            for j, token in enumerate(tokens):
                if token.startswith("repeat(") and token.endswith(")"):
                    # Multiple repeats allowed: fill a share of remaining; reserve consumption for tokens after this repeat.
                    rest_consumption = self._consumption_of_tokens(tokens, j + 1)
                    remaining = noted_markers[i] - consumed - rest_consumption
                    remaining = max(0, remaining)
                    num_repeats_left = len([r for r in repeat_indices if r >= j])
                    fill_count = remaining // num_repeats_left if num_repeats_left else 0
                    leading_sts = len(expanded)
                    inner = token[len("repeat("):-1].strip()
                    inner_tokens = self.split_tokens(inner)
                    # Cap repetitions so we don't consume more than remaining (e.g. repeat(k2) consumes 2 per rep).
                    consumption_per_repeat = self._consumption_of_inner(inner_tokens)
                    if consumption_per_repeat > 0:
                        fill_count = min(fill_count, remaining // consumption_per_repeat)
                    for _ in range(fill_count):
                        for inner_token in inner_tokens:
                            s, count = self.parse_token(inner_token)
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
                                    break
                                consumed += cons
                                produced += prod
                                expanded.insert(leading_sts, s)
                                leading_sts += 1
                            if consumed >= noted_markers[i]:
                                break
                        if consumed >= noted_markers[i]:
                            break
                else:
                    s, count = self.parse_token(token)
                    s = self._normalize_work_est(s)
                    if s == "work_est":
                        if last_row is None or len(last_row) == 0:
                            raise ValueError("'work est' requires a previous row")
                        # Fill segment when token is "work est" or "est" with no number
                        token_lower = token.strip().lower()
                        if count == 1 and token_lower in WORK_EST_ALIASES:
                            rest_consumption = self._consumption_of_tokens(tokens, j + 1)
                            count = noted_markers[i] - consumed - rest_consumption
                            count = max(0, min(count, len(last_row) - consumed))
                        for _ in range(count):
                            if consumed >= len(last_row):
                                raise ValueError(
                                    f"'work est' ran out of previous row "
                                    f"(consumed={consumed}, last_row_len={len(last_row)})"
                                )
                            prev = last_row[consumed]
                            st = self._work_est_stitch(prev, side, is_round)
                            cons, prod = self.CONSUME_PRODUCE["work_est"]
                            if consumed + cons > noted_markers[i]:
                                raise ValueError(
                                    f"Row would consume {consumed + cons} but only "
                                    f"{noted_markers[i]} available"
                                )
                            consumed += cons
                            produced += prod
                            expanded.append(st)
                        continue
                    if s == "inc":
                        num_increases += count
                    elif s == "dec":
                        num_decreases += count
                    if s == "pm":
                        for _ in range(max(count, 1)):
                            markers.append(produced)
                        continue
                    for _ in range(count):
                        # Reject work_est-like tokens that fell through (should have been expanded)
                        if self._normalize_work_est(s) == "work_est":
                            raise ValueError(
                                "'work est' requires a previous row; use after at least one row"
                            )
                        cons, prod = self.CONSUME_PRODUCE.get(s, (1, 1))
                        if consumed + cons > noted_markers[i]:
                            raise ValueError(
                                f"Row would consume {consumed + cons} but only "
                                f"{noted_markers[i]} available"
                            )
                        consumed += cons
                        produced += prod
                        if s == "bo":
                            bind_off_count += 1
                        expanded.append(s)
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
            markers=markers,
            warnings=warnings,
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