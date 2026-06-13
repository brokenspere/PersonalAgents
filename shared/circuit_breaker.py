import time
import functools
import logging

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    logger.info(f"CircuitBreaker half-open for {func.__name__}")
                    self.state = "HALF_OPEN"
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    logger.info(f"CircuitBreaker closed for {func.__name__}")
                    self.state = "CLOSED"
                    self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                logger.warning(f"CircuitBreaker recorded failure for {func.__name__}: {e}")
                
                if self.failures >= self.failure_threshold:
                    logger.error(f"CircuitBreaker OPEN for {func.__name__} after {self.failures} failures")
                    self.state = "OPEN"
                raise
        return wrapper
