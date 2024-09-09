from .v1 import ToolchainsV1
from ..api import CMakeApiType

TOOLCHAINS_API: dict[int, CMakeApiType]  = {
    1: ToolchainsV1,
}
