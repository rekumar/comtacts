import pytest
from unittest.mock import patch
from pathlib import Path
import json

from comtacts.comtacts import add_port, get_port, all_contacts, get_port_with_attributes, delete_contact

def test_add_port(mock_devices, temp_storage_dir):
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        # Add a device at COM3
        add_port("test_device", "COM3")
        
        # Verify the contact file was created
        contact_file = temp_storage_dir / "test_device.json"
        assert contact_file.exists()
        
        # Verify the saved data
        with open(contact_file) as f:
            saved_data = json.load(f)
        assert saved_data["vid"] == "0403"
        assert saved_data["pid"] == "6001"
        assert saved_data["serial_number"] == "A12345"

def test_add_port_not_found(mock_devices, temp_storage_dir):
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        with pytest.raises(ValueError, match="No device found on port COM99"):
            add_port("test_device", "COM99")

def test_get_port(mock_devices, temp_storage_dir):
    # First add a device
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        target_device = mock_devices[0]
        target_port = target_device.device
        add_port("test_device", target_port)
    
    
    # Now try to get its port (it might have moved to a different COM port)
    # Mock that the same device is now on COM8
    modified_devices = mock_devices.copy()
    modified_devices[0].device = "COM8"  # Same device, different port
        
    with patch('serial.tools.list_ports.comports', return_value=modified_devices):
        port = get_port("test_device")
        assert port == "COM8"  # Should find the device at its new location

def test_get_port_device_not_connected(mock_devices, temp_storage_dir):
    # Add a device
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        add_port("test_device", "COM3")
    
    # Try to get its port when it's not connected
    with patch('serial.tools.list_ports.comports', return_value=[]):
        with pytest.raises(ValueError, match="Device 'test_device' is not currently connected"):
            get_port("test_device")

def test_get_port_contact_not_found(temp_storage_dir):
    with pytest.raises(FileNotFoundError, match="No contact found with name: nonexistent"):
        get_port("nonexistent")

def test_get_port_with_attributes(mock_devices):
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        # Find Arduino by manufacturer
        port = get_port_with_attributes(manufacturer="Arduino")
        assert port == "COM5"
        
        # Find specific FTDI device by serial number
        port = get_port_with_attributes(manufacturer="FTDI", serial_number="B67890")
        assert port == "COM4"
        
        # Test with non-existent attributes
        with pytest.raises(ValueError):
            get_port_with_attributes(manufacturer="NonExistent")

def test_all_contacts(mock_devices, temp_storage_dir):
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        # Add two devices
        add_port("device1", "COM3")
        add_port("device2", "COM4")
        
        # Get all contacts
        contacts = all_contacts()
        assert len(contacts) == 2
        assert set(contacts) == {"device1", "device2"}

def test_add_port_overwrite(mock_devices, temp_storage_dir):
    """Test that overwrite flag works as expected when adding ports"""
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        # First add a device at COM3
        add_port("test_device", "COM3")
        
        # Try to add another device with the same name without overwrite flag
        with pytest.raises(ValueError, match="Contact with name 'test_device' already exists!"):
            add_port("test_device", "COM4")
            
        # Now try with overwrite flag
        add_port("test_device", "COM4", overwrite=True)
        
        # Verify the contact file was updated
        contact_file = temp_storage_dir / "test_device.json"
        with open(contact_file) as f:
            saved_data = json.load(f)
        assert saved_data["vid"] == "0403"
        assert saved_data["pid"] == "6001"
        assert saved_data["serial_number"] == "B67890"  # Should have COM4's serial number
        
def test_delete_contact(mock_devices, temp_storage_dir):
    """Test that deleting a contact works as expected"""
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        add_port("test_device", "COM3")
        delete_contact("test_device")
        with pytest.raises(FileNotFoundError, match="No contact found with name: test_device"):
            get_port("test_device")
            
    with pytest.raises(FileNotFoundError, match="No contact found with name: nonexistent"):
        delete_contact("nonexistent")