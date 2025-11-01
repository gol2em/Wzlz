"""
Helper script to find the game process name.

This script lists all running processes and helps you identify
the correct process name for the Wzlz game.
"""

import sys

try:
    import pymem.process
except ImportError:
    print("Error: pymem is not installed")
    print("Install it with: pip install pymem")
    sys.exit(1)


def list_processes():
    """List all running processes."""
    print("Listing all running processes...")
    print("=" * 80)
    print(f"{'PID':<10} {'Process Name':<40} {'Window Title':<30}")
    print("=" * 80)
    
    processes = []
    
    try:
        # Get all process IDs
        for pid in pymem.process.list_processes():
            try:
                # Try to get process name
                process_name = pymem.process.process_from_id(pid).name
                processes.append((pid, process_name))
            except:
                continue
        
        # Sort by name
        processes.sort(key=lambda x: x[1].lower())
        
        # Display
        for pid, name in processes:
            print(f"{pid:<10} {name:<40}")
    
    except Exception as e:
        print(f"Error listing processes: {e}")
        return []
    
    return processes


def search_processes(keyword: str):
    """Search for processes containing a keyword."""
    print(f"\nSearching for processes containing '{keyword}'...")
    print("=" * 80)
    
    found = []
    
    try:
        for pid in pymem.process.list_processes():
            try:
                process_name = pymem.process.process_from_id(pid).name
                if keyword.lower() in process_name.lower():
                    found.append((pid, process_name))
                    print(f"Found: {process_name} (PID: {pid})")
            except:
                continue
    
    except Exception as e:
        print(f"Error searching processes: {e}")
    
    if not found:
        print("No matching processes found.")
    
    return found


def main():
    """Main entry point."""
    print("=" * 80)
    print("Game Process Finder")
    print("=" * 80)
    print()
    
    # Interactive menu
    while True:
        print("\nOptions:")
        print("1. List all processes")
        print("2. Search for process by keyword")
        print("3. Search for 'wzlz' (default)")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            list_processes()
        
        elif choice == '2':
            keyword = input("Enter search keyword: ").strip()
            if keyword:
                search_processes(keyword)
        
        elif choice == '3':
            results = search_processes('wzlz')
            if results:
                print("\nUse one of these process names in your memory reader:")
                for pid, name in results:
                    print(f"  GameMemoryReader(process_name='{name}')")
        
        elif choice == '4':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()

