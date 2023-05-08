
class TestingOnly:
    testing_mode: bool = False

    @classmethod
    def decorator(cls, func):
        def wrapper(*args, **kwargs):
            if not cls.testing_mode:
                raise RuntimeError(f"{func.__name__} is for testing purposes only and should not be called in production.")
            return func(*args, **kwargs)
        return wrapper
    