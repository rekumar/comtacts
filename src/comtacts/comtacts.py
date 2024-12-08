import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

VALID_ATTRIBUTES = ["name", "description", "hwid", "vid", "pid", "serial_number", "location", "manufacturer", "product", "interface"]


def _get_storage_dir() -> Path:
    """Get the directory where contacts are stored.
    
    Returns:
        Path: Directory path where contacts are stored
    """
    custom_dir = os.environ.get("COMTACTS_DIR")
    if custom_dir:
        path = Path(custom_dir)
    else:
        path = Path(__file__).parent / "contacts"
    
    path.mkdir(parents=True, exist_ok=True)
    return path

def _port_to_dict(port_info: ListPortInfo) -> Dict[str, Any]:
    """Convert a ListPortInfo object to a dictionary of its properties. Ignores empty values.
    
    Args:
        port_info (ListPortInfo): Port information object to convert
        
    Returns:
        Dict[str, Any]: Dictionary of non-empty port properties
    """
    port_dict = {key: getattr(port_info, key) for key in VALID_ATTRIBUTES}
    return {k: v for k, v in port_dict.items() if v is not None}

def add_port(name: str, port: str, overwrite: bool = False) -> None:
    """Add a new contact by saving the properties of the specified port.
    
    Args:
        name (str): Name to identify this device
        port (str): Current COM port (e.g., "COM3")
        overwrite (bool): If True, overwrite an existing contact with the same name
    Raises:
        ValueError: If the specified port is not found
    """
    file_path = _get_storage_dir() / f"{name}.json"
    
    if file_path.exists() and not overwrite:
        raise ValueError(f"Contact with name '{name}' already exists! Set overwrite=True to overwrite.")

    for port_info in list_ports.comports():
        if port_info.device == port:
            contact_data = _port_to_dict(port_info)
            
            with open(file_path, "w") as f:
                json.dump(contact_data, f, indent=2)
            return
            
    raise ValueError(f"No device found on port {port}")

def get_port(name: str) -> str:
    """Get the current port for a saved contact.
    
    Args:
        name (str): Name of the saved contact
    
    Returns:
        str: Current COM port (e.g., "COM3")
    
    Raises:
        FileNotFoundError: If no contact exists with the given name
        ValueError: If the device is not currently connected
    """
    file_path = _get_storage_dir() / f"{name}.json"
    
    try:
        with open(file_path, "r") as f:
            saved_props = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"No contact found with name: {name}")

    # Try to find a port that matches the saved properties
    for port_info in list_ports.comports():
        current_props = _port_to_dict(port_info)
        
        # Check if critical identifiers match
        if (saved_props["vid"] == current_props["vid"] and 
            saved_props["pid"] == current_props["pid"] and 
            saved_props["serial_number"] == current_props["serial_number"]):
            return port_info.device
            
    raise ValueError(f"Device '{name}' is not currently connected")

def add_port_with_attributes(name: str, overwrite: bool = False, **kwargs) -> None:
    """Add a new contact by saving the properties of the specified port.
    
    Args:
        name (str): Name to identify this device
        overwrite (bool): If True, overwrite an existing contact with the same name
        **kwargs: Attribute names and values to match against. Attribute names must be valid ListPortInfo attributes. See documentation for serial.tools.list_ports.ListPortInfo for details. 
    """
    for key in kwargs:
        if key not in VALID_ATTRIBUTES:
            raise ValueError(f"{key} is not a valid attribute for ListPortInfo. Valid attributes are: {VALID_ATTRIBUTES}")
            
    file_path = _get_storage_dir() / f"{name}.json"
    
    if file_path.exists() and not overwrite:
        raise ValueError(f"Contact with name '{name}' already exists! Set overwrite=True to overwrite.")
    
    contact_data = {key: value for key, value in kwargs.items() if value is not None}
    
    with open(file_path, "w") as f:
        json.dump(contact_data, f, indent=2)
    
def get_port_with_attributes(**kwargs) -> str:
    """Find a port by matching device attributes.
    
    Args:
        **kwargs: Attribute names and values to match against. Attribute names must be valid ListPortInfo attributes. See documentation for serial.tools.list_ports.ListPortInfo for details. 
    
    Returns:
        str: Current COM port (e.g., "COM3")
    
    Raises:
        ValueError: If no matching device is found
    """
    
    for port_info in list_ports.comports():
        matches = True
        for key, value in kwargs.items():
            try:
                if str(getattr(port_info, key)) != str(value):
                    matches = False
                    break
            except AttributeError:
                raise AttributeError(f"{key} is not a valid attribute for ListPortInfo.")
        if matches:
            return port_info.device
            
    raise ValueError(f"No device found matching attributes: {kwargs}")

def all_contacts() -> List[str]:
    """List all saved contacts.
    
    Returns:
        List[str]: List of contact names
    """
    results = [
        file_path.stem
        for file_path in _get_storage_dir().glob("*.json")
    ]
    
    return results

def delete_contact(name: str) -> None:
    """Delete a contact by name.
    
    Args:
        name (str): Name of the contact to delete
    """
    file_path = _get_storage_dir() / f"{name}.json"
    
    if not file_path.exists():
        raise FileNotFoundError(f"No contact found with name: {name}")
    
    file_path.unlink()
