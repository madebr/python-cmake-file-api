import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum.strenum import StrEnum

class ObjectKind(StrEnum):
    CACHE = "cache"
    CMAKEFILES = "cmakeFiles"
    CODEMODEL = "codemodel"
    CONFIGURELOG = "configureLog"
    TOOLCHAINS = "toolchains"
