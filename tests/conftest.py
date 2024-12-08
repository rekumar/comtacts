import pytest
from pathlib import Path
from unittest.mock import MagicMock
import tempfile
import os

class MockPortInfo:
    """Mock for serial.tools.list_ports.ListPortInfo"""
    def __init__(self, device, vid, pid, serial_number, manufacturer=None, product=None):
        self.device = device
        self.name = device
        self.description = f"Mock device at {device}"
        self.hwid = f"USB VID:PID={vid}:{pid} SER={serial_number}"
        self.vid = vid
        self.pid = pid
        self.serial_number = serial_number
        self.location = None
        self.manufacturer = manufacturer
        self.product = product
        self.interface = None

@pytest.fixture
def mock_devices():
    """Create a set of mock devices for testing"""
    return [
        MockPortInfo("COM3", "0403", "6001", "A12345", "FTDI", "USB-Serial"),
        MockPortInfo("COM4", "0403", "6001", "B67890", "FTDI", "USB-Serial"),
        MockPortInfo("COM5", "2341", "0043", "12345678", "Arduino", "Uno"),
    ]

@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for storing contacts during tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_dir = os.environ.get("COMTACTS_DIR")
        os.environ["COMTACTS_DIR"] = tmpdir
        yield Path(tmpdir)
        if old_dir:
            os.environ["COMTACTS_DIR"] = old_dir
        else:
            del os.environ["COMTACTS_DIR"] 