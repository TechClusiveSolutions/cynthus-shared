"""Answers a request that failed because the signal bus is down."""

from fastapi import Request
from fastapi.responses import JSONResponse

from cynthus.messaging.publisher import SignalBusUnavailable

RETRY_AFTER_SECONDS = 5

CODE = 'service_unavailable'
"""The `code` of the answer: a browser app tells an outage from any other 503 by it."""


def unavailable_response() -> JSONResponse:
    """503 with the single error envelope from the engineering standards, a `code`, and `Retry-After`.

    The text is fixed: the error behind it can name the broker's namespace, which a caller must not see.
    """

    return JSONResponse(
        {'error': 'The service is not available right now. Please try again shortly.', 'code': CODE},
        status_code=503,
        headers={'Retry-After': str(RETRY_AFTER_SECONDS)},
    )


async def signal_bus_unavailable_handler(request: Request, error: SignalBusUnavailable) -> JSONResponse:
    """Answers a request that failed because the signal bus is down."""

    return unavailable_response()
