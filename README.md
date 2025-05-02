# MyPCDetails

A utility for viewing and spoofing PC hardware and software information.

### NOT WIP anymore. Spoofing the BIOS and other information is annoying on your PC and I did not feel like using a VM so this project is delayed/indefinitely archived 

## System Information Checklist

### PC Hardware Identifiers
- [x] Hostname
- [x] MAC Address
- [ ] Motherboard Serial Number
- [ ] BIOS Serial Number
- [ ] Processor ID
- [ ] System UUID
- [ ] Machine GUID
- [ ] ComputerSystem Properties Count

### Disk Information
- [ ] Disk Serial Number
- [ ] Disk Model
- [ ] Volume Serial Number

### OS Information
- [ ] Windows Install Date
- [ ] OS Serial Number
- [ ] User SID

### Network Information
- [x] Local IP Address
- [ ] Public IP Address
- [ ] WLAN GUID
- [x] WLAN Physical Address
- [ ] WLAN BSSID

## Features

- Display all system information in one place
- Spoof MAC address
- Create registry backups before making changes
- Listen for system information changes in real-time

## Usage

```
python app.py [options]
```

### Options
- `--spoof`: Run in spoofer mode
- `--listen`: Enable system information update listener
- `--debug`: Enable debug logging
- `--o`: Save output to a file

### Spoofing CLI Commands
- `mac`: Spoof MAC address
- `backup`: Create registry backup
- `help`: Help
- `info`: Show system information
- `exit`: Exit spoofing mode

## Requirements

- Windows OS (Admin privileges required)
- Python 3.8+
- Required Python packages: see requirements.txt 
