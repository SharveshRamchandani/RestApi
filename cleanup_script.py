import os
import shutil

files = ["APPROACH.md", "Jenkinsfile", "logging.ini"]
dirs = ["data"]

for f in files:
    try:
        if os.path.exists(f):
            os.remove(f)
            print(f"Deleted {f}")
        else:
            print(f"{f} not found")
    except Exception as e:
        print(f"Error deleting {f}: {e}")

for d in dirs:
    try:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"Deleted directory {d}")
        else:
            print(f"{d} not found")
    except Exception as e:
        print(f"Error deleting {d}: {e}")
