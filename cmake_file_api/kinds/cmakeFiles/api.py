from .v1 import CMakeFilesV1
from ..api import CMakeApiType

CMAKEFILES_API: dict[int, CMakeApiType]  = {
    1: CMakeFilesV1,
}
