from .v1 import ConfigureLogV1
from ..api import CMakeApiType

CONFIGURELOG_API: dict[int, CMakeApiType]  = {
    1: ConfigureLogV1,
}
