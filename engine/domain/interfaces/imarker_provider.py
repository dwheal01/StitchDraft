from abc import ABC, abstractmethod
from typing import List

class IMarkerProvider(ABC):
    @abstractmethod
    def get_markers(self, side: str) -> List[int]:
        pass
    
    @abstractmethod
    def move_marker(self, side: str, position: int, shift_amount: int, num_stitches: int) -> None:
        pass
    
    @abstractmethod
    def remove_marker(self, side: str, position: int) -> None:
        pass