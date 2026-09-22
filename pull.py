import os
os.chdir('/home/wlsihszp/gc')
os.system("git fetch origin")
os.system("git reset --hard origin/main")
print("Updated to latest from GitHub.")
