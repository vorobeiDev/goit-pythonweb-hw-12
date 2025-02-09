from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
"""
This module initializes the rate limiter for the FastAPI application.

It uses `slowapi.Limiter` to restrict the number of requests from each client
based on their IP address.

Attributes:
    limiter (Limiter): A rate limiter instance using the remote IP address as the key.
"""