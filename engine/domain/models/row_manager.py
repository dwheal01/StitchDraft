from typing import List

class RowManager:
    """Handles row operations and validation."""
    
    def __init__(self, start_side: str):
        self._rows = []
        self._start_side = start_side
        self._last_row_side = start_side

    def set_last_row_side(self, side: str) -> None:
        self._last_row_side = side
    
    def get_rows(self) -> List[List[str]]:
        """Get all rows (returns defensive copy)."""
        return [list(row) for row in self._rows]
    
    def get_last_row_side(self) -> str:
        """Get the last row side."""
        return self._last_row_side
    
    def get_start_side(self) -> str:
        """Get the starting side."""
        return self._start_side
    
    def get_row_count(self) -> int:
        """Get the number of rows."""
        return len(self._rows)
    
    def get_row(self, index: int) -> List[str]:
        """Get a specific row by index (returns defensive copy)."""
        self._validate_row_index(index)
        return list(self._rows[index])
    
    def update_row(self, index: int, row: List[str]) -> None:
        """Update a specific row by index."""
        self._validate_row_index(index)
        self._rows[index] = list(row)
        
    def add_round(self, row: List[str]) -> None:
        """Add a round to the collection."""
        self._rows.append(row)
    
    def add_row(self, row: List[str], isRound: bool = False) -> None:
        """Add a row to the collection."""
        if self.is_wrong_side(isRound):
            self._last_row_side = "WS"
        else:
            self._last_row_side = "RS"
        self._rows.append(row)
    
    def duplicate_row(self, index: int) -> List[str]:
        """Duplicate an existing row."""
        self._validate_row_index(index)
        return list(self._rows[index])
    
    def is_wrong_side(self, isRound = False) -> bool:
        """Determine if current row should be reversed."""
        if isRound:
            if len(self._rows) == 1:
                return self._last_row_side == "RS"
            return self._last_row_side == "WS"
        else:
            # if len(self._rows) == 0:
            #     return self._start_side == "WS"
            return self._last_row_side == "RS"
            # if self._start_side == "WS":
            #     return len(self._rows) % 2 == 0
            # elif self._start_side == "RS":
            #     return len(self._rows) % 2 != 0
        return False
    
    def reverse_row_if_needed(self, row: List[str], isRound: bool = False) -> List[str]:
        """Reverse row if needed based on knitting direction."""
        if self.is_wrong_side(isRound):
            return row[::-1]
        return row
    
    def _validate_row_index(self, index: int) -> None:
        """Validate row index is within bounds."""
        if index < 0 or index >= len(self._rows):
            raise IndexError(f"Row index {index} out of range")