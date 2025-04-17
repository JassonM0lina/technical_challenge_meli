from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional

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


class InterfaceChain(ABC):

  @abstractmethod
  def set_next(self, handler: InterfaceChain) -> InterfaceChain:
    pass
  @abstractmethod
  def handle(self, request) -> Optional[str]:
    pass


class ContextChain(InterfaceChain):

  _next_handler: InterfaceChain = None


  def __init__(self, parameter: dict) -> None:
    self.repository = parameter
    self.request_resource = self.repository['request_resource']

  #def context_update()

  def set_next(self, handler: InterfaceChain) -> InterfaceChain:
    self._next_handler = handler
    return handler
  
  @abstractmethod
  def handle(self, save_register: dict, chain_step: dict):
    if self._next_handler:
      return self._next_handler.handle(save_register, chain_step)
    #return None