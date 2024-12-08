# COMtacts

This is a tool to remember and detect communication ports using hardware identifiers.

## Usage

### Add a contact

Lets assume you've plugged in a USB device and you know it is currently at port "COM3". We will use COMtacts to remember this hardware so next time you plug it in, we can find it even if its not at "COM3".

```bash
comtacts add --name "My USB Device" --port "COM3"
```

or if you're in python already:

```python
from comtacts import add
add(name="My USB Device", port="COM3")
```

### Get the port of a contact

```bash
comtacts get --name "My USB Device"
```

or if you're in python already:

```python
from comtacts import get_port
get_port(name="My USB Device")
```

Typical usage would be to let your Python script automatically find the port of a device.

```python
from serial import Serial
from comtacts import get_port

ser = Serial(
    port = get_port(name="My USB Device"),
    baudrate = 9600,
    timeout = 1
)
```

### List all contacts

```bash
comtacts all_contacts
```

or if you're in python already:

```python
from comtacts import all_contacts
all_contacts()
```

### Advanced usage -- finding a contact using hardware identifiers

Under the hood, COMtacts uses `serial.tools.list_ports.comports()` to find serial ports. `list_ports.comports()` returns a list of `serial.tools.list_ports.ListPortInfo` objects, which have attributes that can be used to identify a device. If you know the values of these attributes for your device, you can use them to find the port. See the [documentation](<[function](https://pyserial.readthedocs.io/en/latest/tools.html)>) on these functions to see which attributes are available.

For example, if you know the manufacturer, vid, and pid of your device, you can use the `manufacturer`, `vid`, and `pid` attributes to find the port:

```python
from comtacts import get_port_with_attributes
get_port_with_attributes(manufacturer="My Manufacturer", vid="0403", pid="6001")
```

## Making contacts available to all python environments

By default, COMtacts saves contacts _inside its package directory_. This was done such that contacts are specific to a python environment -- most of my use cases are specific to a certain application. If you would like to make contacts available to all python environments, you can set the `COMTACTS_DIR` environment variable to the directory where you would like to save contacts.
