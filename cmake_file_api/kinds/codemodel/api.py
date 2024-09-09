from .v2 import CodemodelV2
from ..api import CMakeApiType

CODEMODEL_API: dict[int, CMakeApiType]  = {
    2: CodemodelV2,
}
