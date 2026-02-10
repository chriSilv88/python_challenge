import random
from datetime import datetime, timedelta

def generate_log(file_path, lines=20_000):
    statuses = ["OK", "OK", "OK", "ERROR", "FORBIDDEN"]
    ips = [
        "192.168.1.1", "192.168.1.2", "192.168.1.3",
        "10.0.0.1", "10.0.0.2",
        "172.16.0.1"
    ]

    start_time = datetime(2024, 1, 1, 0, 0, 0)

    with open(file_path, "w") as f:
        for i in range(lines):
            timestamp = start_time + timedelta(seconds=i)
            bytes_sent = random.choice([0, 512, 1024, 2048, 4096, 8192])
            status = random.choice(statuses)
            ip = random.choice(ips)

            f.write(
                f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')};"
                f"{bytes_sent};{status};{ip}\n"
            )

    print(f"Created file: {file_path} ({lines} lines)")

# --- log generation ---
# small sample log (like sample.log)
generate_log("data/sample.log", lines=20)
# larger realistic log
generate_log("data/requests.log", lines=50_000)