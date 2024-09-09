from .v2 import CacheV2
from ..api import CMakeApiType

CACHE_API: dict[int, CMakeApiType] = {
    2: CacheV2,
}
