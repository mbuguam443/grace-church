import os
# cPanel app root — adjust if your Python app root differs (~/gc by default)
os.chdir(os.path.expanduser('~/gc'))
os.system("git fetch origin")
os.system("git reset --hard origin/main")
print("Updated to latest from GitHub.")
