import os
import string
import itertools

def get_all_drives():
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

def list_startup_files():
    startup_path = os.path.expandvars(r"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    print("\n=== Startup Folder Files ===\n")

    try:
        for item in os.listdir(startup_path):
            print(f"- {item}")
    except FileNotFoundError:
        print("Startup folder not found.")

def search_file(target):
    drives = get_all_drives()
    total = len(drives)

    print(f"\nSearching for anything containing '{target}' across {total} drives...\n")

    spinner = itertools.cycle(["|", "/", "-", "\\"])
    matches = []

    def ignore_errors(error):
        pass

    for index, drive in enumerate(drives, start=1):
        print(f"[{index}/{total}] Scanning {drive}... ", end="", flush=True)

        for root_dir, dirs, files in os.walk(drive, topdown=True, onerror=ignore_errors):
            print(next(spinner), end="\r", flush=True)

            for f in files:
                # CONTAINS MATCHING (case-insensitive)
                if target.lower() in f.lower():
                    matches.append(os.path.join(root_dir, f))

        print("Done.")

    if not matches:
        print("\nNo matching files found.")
        return

    print("\n=== MATCHES FOUND ===")
    for i, path in enumerate(matches, start=1):
        print(f"{i}. {path}")

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

def main():
    while True:
        print("\n=== System File Searcher (CMD Edition) ===")
        print("1. Search for a file")
        print("2. List Startup folder files")
        print("3. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            target = input("Enter part of a file name: ").strip()
            if target:
                search_file(target)
            else:
                print("Please enter a valid file name.")

        elif choice == "2":
            list_startup_files()

        elif choice == "3":
            print("Exiting...")
            break

        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
