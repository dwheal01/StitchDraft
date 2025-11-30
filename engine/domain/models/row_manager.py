from typing import List

class RowManager:
    """Handles row operations and validation."""
    
    def __init__(self, start_side: str):
        self.rows = []
        self.start_side = start_side
        self.last_row_side = start_side

    def set_last_row_side(self, side: str) -> None:
        self.last_row_side = side
        
    def add_round(self, row: List[str]) -> None:
        """Add a round to the collection."""
        self.rows.append(row)
    
    def add_row(self, row: List[str], isRound: bool = False) -> None:
        """Add a row to the collection."""
        if self.is_wrong_side(isRound):
            self.last_row_side = "WS"
        else:
            self.last_row_side = "RS"
        self.rows.append(row)
    
    def duplicate_row(self, index: int) -> List[str]:
        """Duplicate an existing row."""
        self._validate_row_index(index)
        return list(self.rows[index])
    
    def is_wrong_side(self, isRound = False) -> bool:
        """Determine if current row should be reversed."""
        if isRound:
            if len(self.rows) == 1:
                print("first row", self.last_row_side == "RS")
                return self.last_row_side == "RS"
            return self.last_row_side == "WS"
        else:
            # if len(self.rows) == 0:
            #     return self.start_side == "WS"
            return self.last_row_side == "RS"
            # if self.start_side == "WS":
            #     return len(self.rows) % 2 == 0
            # elif self.start_side == "RS":
            #     return len(self.rows) % 2 != 0
        return False
    
    def reverse_row_if_needed(self, row: List[str], isRound: bool = False) -> List[str]:
        """Reverse row if needed based on knitting direction."""
        if self.is_wrong_side(isRound):
            return row[::-1]
        return row
    
    def _validate_row_index(self, index: int) -> None:
        """Validate row index is within bounds."""
        if index < 0 or index >= len(self.rows):
            raise IndexError(f"Row index {index} out of range")