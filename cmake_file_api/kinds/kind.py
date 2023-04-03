import enum


class ObjectKind(enum.Enum):
    CACHE = "cache"
    CMAKEFILES = "cmakeFiles"
    CTESTINFO = "ctestInfo"
    CODEMODEL = "codemodel"
    CONFIGURELOG = "configureLog"
    TOOLCHAINS = "toolchains"
