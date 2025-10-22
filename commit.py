import os
import subprocess
from datetime import datetime
from collections import defaultdict

# Initialize git repo if needed
if not os.path.exists(".git"):
    print("Initializing git repository...")
    subprocess.run(["git", "init"])

# Walk through all files (ignore .git)
files_by_day = defaultdict(list)

for root, dirs, files in os.walk("."):
    if ".git" in dirs:
        dirs.remove(".git")  # ignore .git folder
    for f in files:
        filepath = os.path.join(root, f)
        mtime = os.path.getmtime(filepath)
        day = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        files_by_day[day].append((mtime, filepath))

# Sort days from oldest to newest
sorted_days = sorted(files_by_day.keys())

for day in sorted_days:
    # Get files for this day and sort by time
    day_files = sorted(files_by_day[day], key=lambda x: x[0])
    commit_time = datetime.fromtimestamp(day_files[0][0]).strftime("%Y-%m-%d %H:%M:%S")

    print(f"\nFiles modified on {day}:")
    for _, f in day_files:
        print(f" - {f}")

    commit_msg = input(f"Enter commit message for {day}: ")

    # Stage all files for this day
    for _, f in day_files:
        subprocess.run(["git", "add", f])

    # Commit with earliest timestamp of the day
    env = os.environ.copy()
    env["GIT_COMMITTER_DATE"] = commit_time
    subprocess.run(
        ["git", "commit", "--date", commit_time, "-m", commit_msg],
        env=env
    )

print("\nAll files committed, one commit per day!")
