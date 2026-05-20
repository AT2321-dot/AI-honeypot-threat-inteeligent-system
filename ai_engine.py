def simulate_command(command):
    fake = {
        "ls": "file1.txt  passwords.txt  .bash_history",
        "ls -la": "total 32\ndrwxr-xr-x  4 admin admin  128 Apr 10 12:00 .\n-rw-r--r--  1 admin admin  512 Apr 10 12:00 passwords.txt",
        "whoami": "root",
        "pwd": "/home/admin",
        "cat /etc/passwd": "root:x:0:0:root:/root:/bin/bash\nadmin:x:1000:1000::/home/admin:/bin/bash",
        "uname -a": "Linux honeypot 5.15.0 #1 SMP x86_64 GNU/Linux",
        "id": "uid=0(root) gid=0(root) groups=0(root)",
    }
    return fake.get(command.strip(), "command not found")
