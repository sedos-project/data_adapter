import contextlib

from data_adapter import settings


@contextlib.contextmanager
def turn_on_annotations():
    settings.USE_ANNOTATIONS = True
    try:
        yield
    finally:
        settings.USE_ANNOTATIONS = False
