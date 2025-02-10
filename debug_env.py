# debug_env.py - Environment debugging script
import sys
import subprocess
import pkg_resources


def print_section(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Command: {' '.join(cmd)}")
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except Exception as e:
        print(f"Error running command: {e}")


print_section("Python Information")
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")

print_section("Installed Packages")
installed_packages = [
    f"{dist.key} {dist.version}" for dist in pkg_resources.working_set
]
print("\n".join(sorted(installed_packages)))

print_section("Pytest Version Check")
run_command([sys.executable, "-m", "pytest", "--version"])

print_section("Coverage Installation Check")
run_command([sys.executable, "-m", "pip", "list", "|", "grep", "coverage"])

print_section("Pytest Plugins")
run_command([sys.executable, "-m", "pytest", "--trace-config"])
