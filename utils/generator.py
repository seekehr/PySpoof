import datetime
import random
import uuid

def generate_random_values():
    """
    Generates a dictionary of various random system-like identifiers.

    Returns:
        dict: A dictionary containing randomly generated values for various system attributes.
    """
    values = {
        # Generates a hostname like PC-012345
        "hostname": f"PC-{format(random.randint(0, 999999), '06d')}",

        # Generates a Processor ID in a specific hexadecimal format
        "processor_id": f"BFEBFBFF{format(random.randint(0, 16777215), '06X')}",

        # Generates a standard random UUID (GUID) in uppercase
        "uuid": str(uuid.uuid4()).upper(),

        # Generates a random string mimicking a motherboard serial/model format
        "motherboard": f"{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'S', 'P'])}{random.randint(100, 999)}"
                       f"{random.choice(['N', 'M', 'T', 'X', 'Z'])}{random.choice(['R', 'L', 'K', 'P'])}"
                       f"{random.choice(['C', 'A', 'B', 'E'])}{random.choice(['X', 'Y', 'Z'])}"
                       f"{format(random.randint(0, 9999), '04d')}"
                       f"{random.choice(['F', 'G', 'H'])}{random.choice(['A', 'B', 'C', 'D'])}MB",

        # Generates a random string mimicking a BIOS version format
        "bios": f"{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'S', 'P'])}{random.randint(1, 9)}"
                f"{random.choice(['N', 'M', 'T', 'X', 'Z'])}{random.choice(['R', 'L', 'K', 'P'])}"
                f"{random.choice(['C', 'A', 'B', 'E'])}{random.choice(['X', 'Y', 'Z'])}"
                f"{format(random.randint(0, 9999), '04d')}",

        # Generates a random string mimicking a Windows MachineGuid format
        "machineguid": f"{format(random.randint(0, 16777215), '06x')}{random.choice(['a', 'b', 'c', 'd', 'e', 'f'])}"
                       f"{random.choice(['5', '6', '7', '8'])}{format(random.randint(0, 4095), '03x')}-"
                       f"{format(random.randint(0, 4095), '04x')}-"
                       f"{format(random.randint(0, 4095), '04x')}-"
                       f"{format(random.randint(0, 4095), '04x')}-"
                       f"{format(random.randint(0, 16777215), '06x')}{format(random.randint(0, 255), '02x')}",

        # Generates the current datetime in YYYYMMDDHHMMSS format
        "installdate": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),

        # Generates a random string mimicking an OS serial key format
        "osserial": f"{random.randint(10000, 99999)}-{random.randint(10000, 99999)}-{random.randint(10000, 99999)}",

        # Generates a random string mimicking a Windows Security Identifier (SID) format
        "sid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-"
               f"{random.randint(1000000000, 9999999999)}-"
               f"{random.randint(1000000000, 9999999999)}-"
               f"{random.randint(1000, 9999)}",

        # Generates a random MAC address in colon-separated hexadecimal format
        "mac": ':'.join([format(random.randint(0, 255), '02x') for _ in range(6)]),

        # Generates a standard random UUID (GUID) in lowercase for Wireless LAN
        "wlanguid": str(uuid.uuid4()).lower(),

        # Generates a random BSSID in hyphen-separated hexadecimal format
        "bssid": '-'.join([format(random.randint(0, 255), '02X') for _ in range(6)]),

        # Generates a random string mimicking a disk serial number format
        "diskserial": '_'.join([format(random.randint(0, 65535), '04X') for _ in range(8)]) + '.',

        # Generates a random string mimicking a volume serial number
        "volumeserial": str(random.randint(1000000000, 9999999999)),

        # Generates a random string mimicking a disk model format
        "diskmodel": f"{''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(4))} "
                     f"{''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(2))} "
                     f"{''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(4))}-"
                     f"{random.randint(100, 999)}G"
    }

    # Fix the first byte of the MAC address to be a locally administered, unicast address.
    # The second least significant bit of the first byte determines if it's locally
    # administered (1) or globally administered (0).
    # The least significant bit determines if it's unicast (0) or multicast (1).
    # We set the second LSB to 1 (0x02) and the LSB to 0 (0x00) by ANDing with 0xfe
    # to clear the LSB and ORing with 0x02 to set the second LSB.
    mac_parts = values["mac"].split(':')
    mac_parts[0] = format(int(mac_parts[0], 16) & 0xfe | 0x02, '02x')
    values["mac"] = ':'.join(mac_parts)

    return values

# Example of how to use the function:
# if __name__ == "__main__":
#     random_data = generate_random_values()
#     for key, value in random_data.items():
#         print(f"{key}: {value}")
