"""Main module entrance."""

try:
    from importlib.metadata import version
    __version__ = version('django_jugemaj')
except ModuleNotFoundError:  # Python < 3.7
    pass
