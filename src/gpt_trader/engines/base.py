from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EngineMetadata:
    name: str
    version: str
    deterministic: bool

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("engine name is required")
        if not self.version:
            raise ValueError("engine version is required")


class Engine(ABC):
    @property
    @abstractmethod
    def metadata(self) -> EngineMetadata:
        raise NotImplementedError
