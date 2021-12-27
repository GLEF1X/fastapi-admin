from abc import ABC, abstractmethod
from typing import Optional, cast

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from fastapi_admin.i18n.core import I18n

try:
    from babel import Locale
except ImportError:  # pragma: no cover
    Locale = None


def _get_locale_from_request(request: Request) -> Optional[str]:
    if locale := request.query_params.get("language"):
        return locale
    if locale := request.cookies.get("language"):
        return locale

    if accept_language := request.headers.get("Accept-Language"):
        return accept_language.split(",")[0].replace("-", "_")
    return None


class I18nMiddleware(BaseHTTPMiddleware, ABC):
    """
    Abstract I18n middleware.
    """

    def __init__(self, app: ASGIApp, i18n: I18n, i18n_key: Optional[str] = "i18n",
                 middleware_key: str = "i18n_middleware") -> None:
        """
        Create an instance of middleware
        :param i18n: instance of I18n
        :param i18n_key: context key for I18n instance
        :param middleware_key: context key for this middleware
        """
        super().__init__(app)
        self.i18n = i18n
        self.i18n_key = i18n_key
        self.middleware_key = middleware_key

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        current_locale = await self.get_locale(request) or self.i18n.default_locale

        with self.i18n.context(), self.i18n.use_locale(current_locale):
            return await call_next(request)

    @abstractmethod
    async def get_locale(self, request: Request) -> str:
        """
        Detect current user locale based on request.
        **This method must be defined in child classes**
        :param request:
        :return:
        """
        pass


class SimpleI18nMiddleware(I18nMiddleware):
    """
    Simple I18n middleware.
    Chooses language code from the User object received in event
    """

    def __init__(
            self,
            app: ASGIApp,
            i18n: I18n,
            i18n_key: Optional[str] = "i18n",
            middleware_key: str = "i18n_middleware",
    ) -> None:
        super().__init__(app, i18n=i18n, i18n_key=i18n_key, middleware_key=middleware_key)

        if Locale is None:  # pragma: no cover
            raise RuntimeError(
                f"{type(self).__name__} can be used only when Babel installed\n"
                "Just install Babel (`pip install Babel`) "
                "or aiogram with i18n support (`pip install aiogram[i18n]`)"
            )

    async def get_locale(self, request: Request) -> str:
        if Locale is None:  # pragma: no cover
            raise RuntimeError(
                f"{type(self).__name__} can be used only when Babel installed\n"
                "Just install Babel (`pip install Babel`) "
                "or aiogram with i18n support (`pip install aiogram[i18n]`)"
            )
        locale = _get_locale_from_request(request)
        if locale is None:
            return self.i18n.default_locale

        parsed_locale = Locale.parse(locale)
        if parsed_locale.language not in self.i18n.available_locales:
            return self.i18n.default_locale
        return cast(str, parsed_locale.language)


class ConstI18nMiddleware(I18nMiddleware):
    """
    Const middleware chooses statically defined locale
    """

    def __init__(
            self,
            app: ASGIApp,
            locale: str,
            i18n: I18n,
            i18n_key: Optional[str] = "i18n",
            middleware_key: str = "i18n_middleware",
    ) -> None:
        super().__init__(app, i18n=i18n, i18n_key=i18n_key, middleware_key=middleware_key)
        self.locale = locale

    async def get_locale(self, request: Request) -> str:
        return self.locale
