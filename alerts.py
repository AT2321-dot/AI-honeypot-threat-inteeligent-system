def check_alert(ip, prediction):
    if prediction == "Brute Force":
        print(f"[ALERT] Possible brute force attack from {ip}")
    elif prediction == "Scanning":
        print(f"[ALERT] Port scanning detected from {ip}")
    else:
        print(f"[INFO] Normal activity from {ip}")
