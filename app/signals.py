"""Global signals for application events"""

from PyQt5.QtCore import QObject, pyqtSignal


class SignalManager(QObject):
    """Manages application-wide signals"""
    language_changed = pyqtSignal(str)  # Emitted when language changes


# Global signal manager instance
signal_manager = SignalManager()
