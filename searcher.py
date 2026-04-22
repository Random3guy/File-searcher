import os
import string
import itertools
import sys
import time
from collections import deque

def get_all_drives():
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

# Folders that slow scanning massively
SKIP_FOLDERS = [
    "C:\\Windows\\WinSxS",
    "C:\\Windows\\System32\\DriverStore",
    "C:\\Windows\\SoftwareDistribution",
    "C:\\ProgramData\\Microsoft\\Windows\\Caches"
]

def fast_walk(start_path):
    """Much faster than os.walk() using scandir + queue."""
    queue = deque([start_path])

    while queue:
        current = queue.popleft()

        if any(current.startswith(skip) for skip in SKIP_FOLDERS):
            continue

        try:
            with os.scandir(current) as it:
                dirs = []
                files = []

                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        dirs.append(entry.path)
                    else:
                        files.append(entry.name)

                yield current, dirs, files
                queue.extend(dirs)

        except Exception:
            continue

def list_startup_files():
    startup_path = os.path.expandvars(r"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    print("\n=== Startup Folder Files ===\n")

    try:
        for item in os.listdir(startup_path):
            print(f"- {item}")
    except FileNotFoundError:
        print("Startup folder not found.")

def choose_drive():
    drives = get_all_drives()
    print("\n=== Select Drive ===")
    for i, d in enumerate(drives, start=1):
        print(f"{i}. {d}")
    print(f"{len(drives)+1}. All drives")

    choice = input("\nChoose drive: ").strip()

    if not choice.isdigit():
        return None

    choice = int(choice)

    if 1 <= choice <= len(drives):
        return [drives[choice - 1]]

    if choice == len(drives) + 1:
        return drives

    return None

def search(target, mode):
    drives = choose_drive()
    if not drives:
        print("Invalid drive selection.")
        return

    print(f"\nSearching for {mode}s containing '{target}'...\n")

    spinner = itertools.cycle(["|", "/", "-", "\\"])
    matches = []
    last_spin = time.time()

    for drive in drives:
        print(f"Scanning {drive}... ", end="", flush=True)

        for root_dir, dirs, files in fast_walk(drive):

            # Update spinner every 0.1s
            if time.time() - last_spin > 0.1:
                sys.stdout.write(next(spinner))
                sys.stdout.flush()
                sys.stdout.write("\b")
                last_spin = time.time()

            if mode == "file":
                for f in files:
                    if target.lower() in f.lower():
                        matches.append(os.path.join(root_dir, f))

            elif mode == "folder":
                for d in dirs:
                    folder_name = os.path.basename(d)
                    if target.lower() in folder_name.lower():
                        matches.append(d)

        print("Done.")

    if not matches:
        print("\nNo matches found.")
        return

    print("\n=== MATCHES FOUND ===")
    for i, path in enumerate(matches, start=1):
        print(f"{i}. {path}")

    if mode == "file":
        choice = input("\nDelete a file? Enter number or press Enter to skip: ").strip()

        if not choice:
            print("No files deleted.")
            return

        if not choice.isdigit() or not (1 <= int(choice) <= len(matches)):
            print("Invalid selection.")
            return

        file_to_delete = matches[int(choice) - 1]

        confirm = input(f"Delete '{file_to_delete}'? (y/n): ").strip().lower()
        if confirm == "y":
            try:
                os.remove(file_to_delete)
                print("File deleted successfully.")
            except Exception as e:
                print(f"Failed to delete file: {e}")
        else:
            print("File not deleted.")

def delete_by_path():
    print("\n=== Delete File by Path ===")
    path = input("Enter full file path: ").strip().strip('"')

    if not os.path.isfile(path):
        print("File not found or invalid path.")
        return

    print(f"\nFile found: {path}")
    confirm = input("Delete this file? (y/n): ").strip().lower()

    if confirm == "y":
        try:
            os.remove(path)
            print("File deleted successfully.")
        except Exception as e:
            print(f"Failed to delete file: {e}")
    else:
        print("File not deleted.")

def main():
    while True:
        print("\n=== System File Searcher (CMD Edition) ===")
        print("1. Search for a file")
        print("2. Search for a folder")
        print("3. List Startup folder files")
        print("4. Delete file by path")
        print("5. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            target = input("Enter part of a file name: ").strip()
            if target:
                search(target, "file")

        elif choice == "2":
            target = input("Enter part of a folder name: ").strip()
            if target:
                search(target, "folder")

        elif choice == "3":
            list_startup_files()

        elif choice == "4":
            delete_by_path()

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
