import pythoncom
import wmi

def spoof_mac():
    pythoncom.CoInitialize()
    wm = wmi.WMI()

# ================================
# Main Function and CLI Interface
# ================================

def print_help():
    """Print help information for all spoofing functions"""
    print(f"{INFO} MyPCDetails System Spoofer - Help Information")
    print("\nAvailable spoofing commands:")
    
    print("\n=== PC Information Spoofing ===")
    print("  hostname <new_hostname>            - Spoof system hostname")
    print("  processor <new_processor_id>       - Spoof processor ID")
    print("  uuid <new_uuid>                    - Spoof system UUID")
    print("  motherboard <new_serial>           - Spoof motherboard serial")
    print("  bios <new_serial>                  - Spoof BIOS serial number")
    print("  machineguid <new_guid>             - Spoof Machine GUID")
    
    print("\n=== OS Information Spoofing ===")
    print("  installdate <YYYYMMDDHHMMSS>       - Spoof Windows installation date")
    print("  osserial <new_serial>              - Spoof OS serial/product key")
    print("  sid <new_sid>                      - Spoof User SID")
    
    print("\n=== Network Information Spoofing ===")
    print("  mac <new_mac> [interface]          - Spoof MAC address (random if not specified)")
    print("  wlanguid <new_guid>                - Spoof WLAN interface GUID")
    print("  bssid <new_bssid>                  - Spoof WLAN BSSID (router MAC)")
    
    print("\n=== Disk Information Spoofing ===")
    print("  diskserial <new_serial>            - Spoof disk serial number")
    print("  volumeserial <new_serial> [drive]  - Spoof volume serial (default: C:)")
    print("  diskmodel <new_model>              - Spoof disk model name")
    
    print("\n=== Special Commands ===")
    print("  spoofall <profile>                 - Apply all spoofing from preset or json profile")
    print("  randomize                          - Randomize all possible values")
    print("  help                               - Display this help information")
    
    print("\nExamples:")
    print("  python spoofer.py hostname SecHex-ZANBNZW")
    print("  python spoofer.py mac 00:15:5D:E4:5E:E2")
    print("  python spoofer.py diskmodel \"NVMe WD PC SN740 SDDPNQD-512G-1002\"")
    print("  python spoofer.py spoofall example-profile.json")
    
    print(f"\n{WARNING} Administrator privileges required for most operations.")

def generate_random_values():
    """Generate random values for all spoofable attributes"""
    import random
    import uuid
    
    values = {
        "hostname": f"PC-{format(random.randint(0, 999999), '06d')}",
        "processor_id": f"BFEBFBFF{format(random.randint(0, 16777215), '06X')}",
        "uuid": str(uuid.uuid4()).upper(),
        "motherboard": f"{random.choice(['A','B','C','D','E','F','S','P'])}{random.randint(100, 999)}"
                      f"{random.choice(['N','M','T','X','Z'])}{random.choice(['R','L','K','P'])}"
                      f"{random.choice(['C','A','B','E'])}{random.choice(['X','Y','Z'])}"
                      f"{format(random.randint(0, 9999), '04d')}"
                      f"{random.choice(['F','G','H'])}{random.choice(['A','B','C','D'])}MB",
        "bios": f"{random.choice(['A','B','C','D','E','F','S','P'])}{random.randint(1, 9)}"
               f"{random.choice(['N','M','T','X','Z'])}{random.choice(['R','L','K','P'])}"
               f"{random.choice(['C','A','B','E'])}{random.choice(['X','Y','Z'])}"
               f"{format(random.randint(0, 9999), '04d')}",
        "machineguid": f"{format(random.randint(0, 16777215), '06x')}{random.choice(['a','b','c','d','e','f'])}"
                      f"{random.choice(['5','6','7','8'])}{format(random.randint(0, 4095), '03x')}-"
                      f"{format(random.randint(0, 4095), '04x')}-"
                      f"{format(random.randint(0, 4095), '04x')}-"
                      f"{format(random.randint(0, 4095), '04x')}-"
                      f"{format(random.randint(0, 16777215), '06x')}{format(random.randint(0, 255), '02x')}",
        "installdate": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "osserial": f"{random.randint(10000, 99999)}-{random.randint(10000, 99999)}-{random.randint(10000, 99999)}",
        "sid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-"
              f"{random.randint(1000000000, 9999999999)}-"
              f"{random.randint(1000000000, 9999999999)}-"
              f"{random.randint(1000, 9999)}",
        "mac": ':'.join([format(random.randint(0, 255), '02x') for _ in range(6)]),
        "wlanguid": str(uuid.uuid4()).lower(),
        "bssid": '-'.join([format(random.randint(0, 255), '02X') for _ in range(6)]),
        "diskserial": '_'.join([format(random.randint(0, 65535), '04X') for _ in range(8)]) + '.',
        "volumeserial": str(random.randint(1000000000, 9999999999)),
        "diskmodel": f"{''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(4))} "
                    f"{''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(2))} "
                    f"{''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(4))}-"
                    f"{random.randint(100, 999)}G"
    }
    
    # Fix first byte of MAC to be a locally administered, unicast address
    mac_parts = values["mac"].split(':')
    mac_parts[0] = format(int(mac_parts[0], 16) & 0xfe | 0x02, '02x')
    values["mac"] = ':'.join(mac_parts)
    
    return values

def spoof_from_profile(profile_path=None):
    """Apply all spoofing settings from a profile"""
    import json
    from datetime import datetime
    
    # If no profile provided, use example values
    if not profile_path:
        # Example values from the requirement
        values = {
            "hostname": "SecHex-ZANBNZW",
            "processor_id": "BFEBFBFF000906A3",
            "uuid": "479B2D2D-E804-CB47-BA81-C5CB1787069F",
            "motherboard": "S311NRCX0031FAMB",
            "bios": "S3NRCX01L007116",
            "machineguid": "4615e549-s566-q721-j499-f3149d89",
            "installdate": "20241213162931",
            "osserial": "67489-63188-60292-X0",
            "sid": "S-1-5-21-1103905739-3479899694-3139268737-1001",
            "mac": "00:15:5D:E4:5E:E2",
            "wlanguid": "39fb4fd8-51bb-4520-83a4-3e572a2d3b2e",
            "wlanaddr": "FE-53-12-16-A2-03",
            "bssid": "70-8C-B6-E3-4A-E8",
            "diskserial": "E823_8FA6_BF53_0001_001B_448B_474B_9D8D.",
            "volumeserial": "1446379651",
            "diskmodel": "NVMe WD PC SN740 SDDPNQD-512G-1002"
        }
    else:
        # Load values from JSON profile
        try:
            with open(profile_path, 'r') as f:
                values = json.load(f)
        except Exception as e:
            print(f"{ERROR} Failed to load profile: {e}")
            return False
    
    # Apply each spoofing function with values from profile
    success_count = 0
    total_count = 0
    
    print(f"{INFO} Starting system spoofing process...")
    
    # PC Information
    if "hostname" in values:
        total_count += 1
        if spoof_hostname(values["hostname"]):
            success_count += 1
    
    if "processor_id" in values:
        total_count += 1
        if spoof_processor_id(values["processor_id"]):
            success_count += 1
    
    if "uuid" in values:
        total_count += 1
        if spoof_uuid(values["uuid"]):
            success_count += 1
    
    if "motherboard" in values:
        total_count += 1
        if spoof_motherboard(values["motherboard"]):
            success_count += 1
    
    if "bios" in values:
        total_count += 1
        if spoof_bios(values["bios"]):
            success_count += 1
    
    if "machineguid" in values:
        total_count += 1
        if spoof_machine_guid(values["machineguid"]):
            success_count += 1
    
    # OS Information
    if "installdate" in values:
        total_count += 1
        if spoof_os_install_date(values["installdate"]):
            success_count += 1
    
    if "osserial" in values:
        total_count += 1
        if spoof_os_serial(values["osserial"]):
            success_count += 1
    
    if "sid" in values:
        total_count += 1
        if spoof_user_sid(values["sid"]):
            success_count += 1
    
    # Network Information
    if "mac" in values:
        total_count += 1
        if spoof_mac(values["mac"]):
            success_count += 1
    
    if "wlanguid" in values:
        total_count += 1
        if spoof_wlan_guid(values["wlanguid"]):
            success_count += 1
    
    if "bssid" in values:
        total_count += 1
        if spoof_wlan_bssid(values["bssid"]):
            success_count += 1
    
    # Disk Information
    if "diskserial" in values:
        total_count += 1
        if spoof_disk_serial(values["diskserial"]):
            success_count += 1
    
    if "volumeserial" in values:
        total_count += 1
        if spoof_volume_serial(values["volumeserial"]):
            success_count += 1
    
    if "diskmodel" in values:
        total_count += 1
        if spoof_disk_model(values["diskmodel"]):
            success_count += 1
    
    print(f"\n{INFO} Spoofing complete: {success_count}/{total_count} operations successful.")
    
    if success_count < total_count:
        print(f"{WARNING} Some operations failed. Administrator privileges may be required.")
        print(f"{INFO} Restart your computer for all changes to take effect.")
    else:
        print(f"{SUCCESS} All operations completed successfully.")
        print(f"{INFO} Restart your computer for all changes to take effect.")
    
    return success_count == total_count

def main():
    """Main entry point for the spoofing script"""
    import sys
    
    # Check for admin privileges
    if not is_admin():
        print(f"{WARNING} Running without administrator privileges.")
        print(f"{WARNING} Some spoofing operations may fail. Run as administrator for full functionality.")
    
    # Print help if no arguments or help requested
    if len(sys.argv) <= 1 or sys.argv[1].lower() in ['-h', '--help', 'help']:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    # PC Information spoofing
    if command == 'hostname' and len(sys.argv) > 2:
        spoof_hostname(sys.argv[2])
    elif command == 'processor' and len(sys.argv) > 2:
        spoof_processor_id(sys.argv[2])
    elif command == 'uuid' and len(sys.argv) > 2:
        spoof_uuid(sys.argv[2])
    elif command == 'motherboard' and len(sys.argv) > 2:
        spoof_motherboard(sys.argv[2])
    elif command == 'bios' and len(sys.argv) > 2:
        spoof_bios(sys.argv[2])
    elif command == 'machineguid' and len(sys.argv) > 2:
        spoof_machine_guid(sys.argv[2])
    
    # OS Information spoofing
    elif command == 'installdate' and len(sys.argv) > 2:
        spoof_os_install_date(sys.argv[2])
    elif command == 'osserial' and len(sys.argv) > 2:
        spoof_os_serial(sys.argv[2])
    elif command == 'sid' and len(sys.argv) > 2:
        spoof_user_sid(sys.argv[2])
    
    # Network Information spoofing
    elif command == 'mac':
        if len(sys.argv) > 3:
            spoof_mac(sys.argv[2], sys.argv[3])
        elif len(sys.argv) > 2:
            spoof_mac(sys.argv[2])
        else:
            spoof_mac()  # Random MAC
    elif command == 'wlanguid' and len(sys.argv) > 2:
        spoof_wlan_guid(sys.argv[2])
    elif command == 'bssid' and len(sys.argv) > 2:
        spoof_wlan_bssid(sys.argv[2])
    
    # Disk Information spoofing
    elif command == 'diskserial' and len(sys.argv) > 2:
        spoof_disk_serial(sys.argv[2])
    elif command == 'volumeserial':
        if len(sys.argv) > 3:
            spoof_volume_serial(sys.argv[2], sys.argv[3])
        elif len(sys.argv) > 2:
            spoof_volume_serial(sys.argv[2])
        else:
            print(f"{ERROR} Volume serial number required.")
    elif command == 'diskmodel' and len(sys.argv) > 2:
        spoof_disk_model(sys.argv[2])
    
    # Special commands
    elif command == 'spoofall':
        if len(sys.argv) > 2:
            spoof_from_profile(sys.argv[2])
        else:
            spoof_from_profile()  # Use default values
    elif command == 'randomize':
        random_values = generate_random_values()
        print(f"{INFO} Generated random values:")
        for key, value in random_values.items():
            print(f"  {key}: {value}")
        
        user_confirm = input(f"\n{INFO} Do you want to apply these random values? (y/n): ")
        if user_confirm.lower() in ['y', 'yes']:
            # Convert the dictionary to a temporary JSON file
            import tempfile
            import json
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w')
            json.dump(random_values, temp_file)
            temp_file.close()
            
            # Apply the profile
            spoof_from_profile(temp_file.name)
            
            # Clean up
            import os
            os.unlink(temp_file.name)
    else:
        print(f"{ERROR} Unknown command: {command}")
        print_help()

if __name__ == "__main__":
    # Import datetime here to ensure it's available for both functions
    import datetime
    
    # Add constants for colorama if they aren't already defined
    try:
        # Test if constants are defined
        if SUCCESS and WARNING and ERROR and INFO:
            pass
    except NameError:
        # Define them if they weren't imported
        from colorama import Fore, Style
        SUCCESS = Fore.GREEN + "[SUCCESS]" + Style.RESET_ALL
        WARNING = Fore.YELLOW + "[WARNING]" + Style.RESET_ALL
        ERROR = Fore.RED + "[ERROR]" + Style.RESET_ALL
        INFO = Fore.BLUE + "[INFO]" + Style.RESET_ALL
    
    main()
