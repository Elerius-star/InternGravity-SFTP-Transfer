import paramiko
import os

def connect_sftp(hostname, port, username, password):
    try:
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print(f"\n✅ Connected to {hostname} successfully.\n")
        return sftp, transport
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return None, None

def list_files(sftp, remote_path="."):
    try:
        files = sftp.listdir(remote_path)
        print(f"\n📁 Files in '{remote_path}':")
        for f in files:
            print(f"   - {f}")
    except Exception as e:
        print(f"\n❌ Failed to list files: {e}")

def upload_file(sftp, local_path, remote_path):
    try:
        sftp.put(local_path, remote_path)
        print(f"\n⬆️  Uploaded '{local_path}' to '{remote_path}'")
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")

def download_file(sftp, remote_path, local_path):
    try:
        sftp.get(remote_path, local_path)
        print(f"\n⬇️  Downloaded '{remote_path}' to '{local_path}'")
    except Exception as e:
        print(f"\n❌ Download failed: {e}")

def main():
    print("🔐 SFTP Client - Secure File Transfer")
    hostname = input("Server IP or Hostname: ")
    port = int(input("Port (usually 22): "))
    username = input("Username: ")
    password = input("Password: ")

    sftp, transport = connect_sftp(hostname, port, username, password)
    if not sftp:
        return

    while True:
        print("""
🔧 Choose an action:
1. List Files on Server
2. Upload File to Server
3. Download File from Server
4. Exit
""")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            remote_path = input("Remote path to list (default: .): ") or "."
            list_files(sftp, remote_path)

        elif choice == "2":
            local_path = input("Local file to upload: ")
            remote_path = input("Remote destination path: ")
            upload_file(sftp, local_path, remote_path)

        elif choice == "3":
            remote_path = input("Remote file to download: ")
            local_path = input("Local destination path: ")
            download_file(sftp, remote_path, local_path)

        elif choice == "4":
            print("👋 Disconnecting...")
            sftp.close()
            transport.close()
            break

        else:
            print("❗ Invalid option. Please choose 1–4.")

if __name__ == "__main__":
    main()
