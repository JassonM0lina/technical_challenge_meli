from abc import ABC, abstractmethod


class InterfaceConnection(ABC):

  @abstractmethod
  def request(self) -> None:
      pass

class InterfaceCRUDCommand(ABC):

  @abstractmethod
  def operation(self, obj_get_meli_data: InterfaceConnection) -> None:
      pass

