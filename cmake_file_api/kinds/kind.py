import enum


class ObjectKind(enum.Enum):
    CACHE = "cache"
    CMAKEFILES = "cmakeFiles"
    CODEMODEL = "codemodel"
    CONFIGURELOG = "configureLog"
    TOOLCHAINS = "toolchains"
