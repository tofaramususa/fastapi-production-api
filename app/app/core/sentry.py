"""
Sentry integration configuration for the application.
Handles initialization and setup of Sentry monitoring.
"""

import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """
    Initialize Sentry SDK with appropriate configuration.
    Only initializes in production environment.
    """
    if not settings.PRODUCTION:
        return

    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            # Add data like request headers and IP for users,
            # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
            send_default_pii=True,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for tracing.
            traces_sample_rate=1.0,
            _experiments={
                # Set continuous_profiling_auto_start to True
                # to automatically start the profiler on when
                # possible.
                "continuous_profiling_auto_start": True,
            },
            integrations=[
                StarletteIntegration(
                    transaction_style="url",
                    failed_request_status_codes=set(range(400, 600)),
                    http_methods_to_capture=("GET", "POST"),
                ),
                FastApiIntegration(
                    transaction_style="url",
                    failed_request_status_codes=set(range(400, 600)),
                    http_methods_to_capture=("GET", "POST"),
                ),
            ],
        )
        logger.info("Sentry initialized successfully in production mode")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {str(e)}")
        # Continue without Sentry - don't crash the application
