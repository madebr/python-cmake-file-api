from .kind import ObjectKind
from .cache.api import CACHE_API
from .cmakeFiles.api import CMAKEFILES_API
from .codemodel.api import CODEMODEL_API


OBJECT_KINDS_API = {
    ObjectKind.CACHE: CACHE_API,
    ObjectKind.CMAKEFILES: CMAKEFILES_API,
    ObjectKind.CODEMODEL: CODEMODEL_API,
}
