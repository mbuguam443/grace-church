#!/usr/bin/env python3
"""
Grace Church Munyaka - Git-based Updater
=========================================
Update the live server to the latest code from GitHub, no zip needed.

How to run (in the app folder, e.g. where manage.py / passenger_wsgi.py live):
    python3 update.py
    # or, from the Python venv cPanel created:
    source venv/bin/activate && python update.py

What it does
------------
1. Adopts this folder as a git checkout on first run (converts the existing
   file-based install in place, keeping media/, .env and the database).
2. git fetch + hard reset to origin/main (local edits are discarded on purpose;
   git is the source of truth).
3. Installs any new Python packages from requirements.txt (best effort).
4. Runs migrations and collects static files.
5. Touches tmp/restart.txt so Passenger reloads the app.

Files that intentionally stay OUT of git and are never touched by this script:
    media/uploads/        (church files you uploaded via Church Settings)
    .env                  (database passwords, secret keys)
    db.sqlite3 / *.log    (local dev leftovers / logs)
    staticfiles/          (collectstatic output, rebuilt on every run)
"""
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GIT_URL = "https://github.com/mbuguam443/grace-church.git"

os.chdir(BASE_DIR)


def run(cmd, check=True, env=None):
    print("$ " + " ".join(cmd))
    full_env = dict(os.environ)
    full_env.update(env or {})
    r = subprocess.run(cmd, cwd=BASE_DIR, env=full_env, text=True)
    if check and r.returncode != 0:
        sys.exit("\n[ERROR] Command failed: " + " ".join(cmd))
    return r


def git(*args, check=True):
    return run(["git"] + list(args), check=check)


def main():
    print("=" * 56)
    print(" Grace Church Munyaka - Git updater")
    print("=" * 56)

    # 0) git must be available
    r = git("--version", check=False)
    if r.returncode != 0:
        sys.exit(
            "\n[ERROR] git is not installed / not available in this shell.\n"
            "Enable git + SSH (cPanel -> Terminal) or use a cPanel plan with\n"
            "'Git Version Control'. Alternatively keep deploying via the zip."
        )

    # 1) Convert to a git checkout on first run
    if not os.path.isdir(os.path.join(BASE_DIR, ".git")):
        print("\n[1/5] First run - adopting this folder as a git checkout ...")
        git("init")
        git("checkout", "-B", "main", check=False)  # deterministic branch name
        git("remote", "add", "origin", GIT_URL, check=False)
        git("fetch", "origin")
        # Adopt the current server files as a local commit so the reset below
        # can overwrite them cleanly. media/, .env and db are git-ignored, so
        # they are staged out and survive every update.
        git("add", "-A")
        git(
            "-c", "user.name=Deployer",
            "-c", "user.email=deploy@gracechurch",
            "commit", "-m", "Adopt server tree (pre-git install)",
            check=False,
        )
        git("reset", "--hard", "origin/main")
        print("    Checkout ready.")
    else:
        print("\n[1/5] Updating from GitHub ...")
        git("fetch", "origin")
        git("reset", "--hard", "origin/main")

    commit = git("rev-parse", "--short", "HEAD", check=False)
    print("    Now at origin/main @ %s" % commit.stdout.strip())

    # 2) New dependencies (best effort - never fail the update for this)
    print("[2/5] Installing requirements ...")
    run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"], check=False)

    # 3) Migrations + static files
    print("[3/5] Migrations ...")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fbms.settings_production")
    try:
        import django

        django.setup()
        from django.core.management import call_command

        call_command("migrate", interactive=False)
        print("[4/5] Collecting static files ...")
        call_command("collectstatic", "--noinput")
    except Exception as exc:
        sys.exit("\n[ERROR] Django step failed: %s\n"
                 "Run this script with the SAME python the app uses (its venv)." % exc)

    # 4) Ask Passenger to reload
    print("[5/5] Triggering app reload (tmp/restart.txt) ...")
    os.makedirs(os.path.join(BASE_DIR, "tmp"), exist_ok=True)
    with open(os.path.join(BASE_DIR, "tmp", "restart.txt"), "w") as f:
        f.write("")

    print("\n" + "=" * 56)
    print(" UPDATE COMPLETE  (@%s)" % commit.stdout.strip())
    print("=" * 56)
    print(" If the site still looks old: cPanel -> Setup Python App -> Restart,")
    print(" then hard-refresh the browser (Ctrl+F5) once.")


if __name__ == "__main__":
    main()