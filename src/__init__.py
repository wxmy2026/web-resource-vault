"""Web Resource Vault public API."""

from .vault import DownloadError, ResourceVault, RobotsDenied

__all__ = ["DownloadError", "ResourceVault", "RobotsDenied"]
__version__ = "0.2.0"
