import pkg_resources

from gns3fy.server import Server

__version__ = pkg_resources.get_distribution("gns3fy").version


__all__ = ["Server", "__version__"]
