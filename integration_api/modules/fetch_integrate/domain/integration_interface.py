from __future__ import annotations
from abc import ABC, abstractmethod

class ContextState:

    _state = None

    def __init__(self, parameter: dict) -> None:
      self.repository = parameter

    def transition_to(self, state: InterfaceState):

        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def request(self, *args, **kwargs):
        self._state.handle(*args, **kwargs)

class InterfaceState(ABC):

    @property
    def context(self) -> ContextState:
        return self._context

    @context.setter
    def context(self, context: ContextState) -> None:
        self._context = context

    @abstractmethod
    def handle(self) -> None:
        pass

class InterfaceConnection(ABC):

  @abstractmethod
  def request(self) -> None:
      pass