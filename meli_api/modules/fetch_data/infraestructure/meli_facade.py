from modules.fetch_data.domain.meli_constant import EnvConstant
from modules.fetch_data.application.meli_crud_operation import ReadDataOperation
from modules.fetch_data.infraestructure.meli_connection import FileExtract


class MeliApiFacade:

  def __init__(self, parameter: dict):
    self.parameter = parameter

  def operation(self):
    
    name_file: str = self.parameter['name_file']
    total_id: list = self.parameter['total_id']
    total_attributes: list = self.parameter.get('total_attributes',[])

    location_file = f'{EnvConstant.STR_LOCATION_DATA}/{name_file}'

    obj_file_extract = FileExtract(location_file)
    obj_crud_operation = ReadDataOperation(total_id, total_attributes)
    register = obj_crud_operation.operation(obj_file_extract)
    return register
