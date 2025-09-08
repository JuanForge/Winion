from typing import Literal
class VERSION:
    VERSION = "0.0.1-alpha"
    BUILD = "2025.09.08:23.22"
    RELEASE = 'DEV'

    @staticmethod
    def version() -> str:
        return VERSION.VERSION

    @staticmethod
    def build() -> str:
        return VERSION.BUILD

    @staticmethod
    def release() -> Literal['DEBUG', 'BETA', 'RELEASE', 'ALPHA', "DEV"]:
        return VERSION.RELEASE