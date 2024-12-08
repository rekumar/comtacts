import pytest
from unittest.mock import patch
import json
from pathlib import Path
from click.testing import CliRunner
from comtacts.cli import cli

def test_cli_add(mock_devices, temp_storage_dir):
    runner = CliRunner()
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        result = runner.invoke(cli, ['add', '--name', 'test_device', '--port', 'COM3'])
        assert result.exit_code == 0
        assert "Added contact 'test_device' for port COM3" in result.output
        
        # Verify file was created
        contact_file = temp_storage_dir / "test_device.json"
        assert contact_file.exists()
        
        # try a non-existent port
        result = runner.invoke(cli, ['add', '--name', 'missing_device', '--port', 'COM99'])
        assert result.exit_code == 1
        assert "Error: No device found on port COM99" in result.output

def test_cli_get(mock_devices, temp_storage_dir):
    runner = CliRunner()
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        # First add a device
        port = mock_devices[0].device
        result = runner.invoke(cli, ['add', '--name', 'test_device', '--port', port])
        assert result.exit_code == 0
        
        # Now try to get its port
        result = runner.invoke(cli, ['get', '--name', 'test_device'])
        assert result.exit_code == 0
        assert port in result.output
    
    # now move the device to COM8 and ensure we get the new port
    mock_devices[0].device = "COM8"
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        result = runner.invoke(cli, ['get', '--name', 'test_device'])
        assert result.exit_code == 0
        assert "COM8" in result.output

def test_cli_all(mock_devices, temp_storage_dir):
    runner = CliRunner()
    result = runner.invoke(cli, ['all'])
    assert result.exit_code == 0
    assert "No contacts found" in result.output
    
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        # Add two devices
        result = runner.invoke(cli, ['add', '--name', 'device1', '--port', 'COM3'])
        assert result.exit_code == 0
        result = runner.invoke(cli, ['add', '--name', 'device2', '--port', 'COM4'])
        assert result.exit_code == 0
            
        # List all contacts
        result = runner.invoke(cli, ['all'])
        assert result.exit_code == 0
        assert "device1" in result.output
        assert "device2" in result.output

def test_cli_where(temp_storage_dir):
    runner = CliRunner()
    result = runner.invoke(cli, ['where'])
    assert result.exit_code == 0
    assert str(temp_storage_dir) in result.output

def test_cli_add_overwrite(mock_devices, temp_storage_dir):
    """Test the --overwrite flag in the CLI"""
    runner = CliRunner()
    with patch('serial.tools.list_ports.comports', return_value=mock_devices):
        # First add a device
        result = runner.invoke(cli, ['add', '--name', 'test_device', '--port', 'COM3'])
        assert result.exit_code == 0
        
        # Try to add another device with the same name without overwrite flag
        result = runner.invoke(cli, ['add', '--name', 'test_device', '--port', 'COM4'])
        assert result.exit_code == 1
        assert "Error: Contact with name 'test_device' already exists" in result.output
        
        # Now try with overwrite flag
        result = runner.invoke(cli, ['add', '--name', 'test_device', '--port', 'COM4', '--overwrite'])
        assert result.exit_code == 0
        assert "Added contact 'test_device' for port COM4" in result.output
        
        # Verify the contact was updated
        contact_file = temp_storage_dir / "test_device.json"
        with open(contact_file) as f:
            saved_data = json.load(f)
        assert saved_data["serial_number"] == "B67890"  # Should have COM4's serial number