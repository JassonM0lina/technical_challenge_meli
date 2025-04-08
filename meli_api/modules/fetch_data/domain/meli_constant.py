from dataclasses import dataclass
import os

@dataclass(frozen=True)
class EnvConstant:
    
  STR_LOCATION_DATA: str = os.path.join(os.path.dirname(__file__), 'assets')