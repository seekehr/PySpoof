import datetime
import random
import uuid


def generate_random_values():
    values = {
        "hostname": f"PC-{format(random.randint(0, 999999), '06d')}",
        "processor_id": f"BFEBFBFF{format(random.randint(0, 16777215), '06X')}",
        "uuid": str(uuid.uuid4()).upper(),
        "motherboard": f"{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'S', 'P'])}{random.randint(100, 999)}"
                       f"{random.choice(['N', 'M', 'T', 'X', 'Z'])}{random.choice(['R', 'L', 'K', 'P'])}"
                       f"{random.choice(['C', 'A', 'B', 'E'])}{random.choice(['X', 'Y', 'Z'])}"
                       f"{format(random.randint(0, 9999), '04d')}"
                       f"{random.choice(['F', 'G', 'H'])}{random.choice(['A', 'B', 'C', 'D'])}MB",
        "bios": f"{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'S', 'P'])}{random.randint(1, 9)}"
                f"{random.choice(['N', 'M', 'T', 'X', 'Z'])}{random.choice(['R', 'L', 'K', 'P'])}"
                f"{random.choice(['C', 'A', 'B', 'E'])}{random.choice(['X', 'Y', 'Z'])}"
                f"{format(random.randint(0, 9999), '04d')}",
        "machineguid": f"{format(random.randint(0, 16777215), '06x')}{random.choice(['a', 'b', 'c', 'd', 'e', 'f'])}"
                       f"{random.choice(['5', '6', '7', '8'])}{format(random.randint(0, 4095), '03x')}-"
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