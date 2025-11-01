"""Quick script to find the process name containing '五子连珠'"""
import win32gui
import win32process
import psutil

def find_process_by_window_title(title_substring):
    """Find process name by window title"""
    def callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title_substring in window_title:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    results.append({
                        'window_title': window_title,
                        'process_name': process.name(),
                        'pid': pid,
                        'exe': process.exe()
                    })
                except:
                    pass
        return True
    
    results = []
    win32gui.EnumWindows(callback, results)
    return results

if __name__ == "__main__":
    print("Searching for processes with '五子连珠' in window title...")
    results = find_process_by_window_title("五子连珠")
    
    if results:
        print(f"\nFound {len(results)} matching process(es):\n")
        for r in results:
            print(f"Window Title: {r['window_title']}")
            print(f"Process Name: {r['process_name']}")
            print(f"PID: {r['pid']}")
            print(f"Executable: {r['exe']}")
            print("-" * 60)
    else:
        print("\nNo matching processes found. Make sure the game is running!")

