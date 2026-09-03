from abc import ABC, abstractmethod
from typing import Tuple

class BaseUploader(ABC):
    @abstractmethod
    def upload(self, video_path: str, caption: str, **kwargs) -> Tuple[bool, dict]:
        """Return (success, metadata)"""
        pass
