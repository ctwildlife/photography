import subprocess

# List of the Python scripts you want to run, in the correct order
scripts = [
    "generate_galleries.py",
    "recent_photos.py",
    "inject_static.py",
    "remove_amps.py",
    "inject_nav.py"
]

def run_scripts_in_sequence():
    for script in scripts:
        print(f"Running {script}...")
        # Run each script in sequence
        try:
            subprocess.run(['python', script], check=True)
            print(f"Finished {script}")
        except subprocess.CalledProcessError as e:
            print(f"Error running {script}: {e}")
            break  # Stop running scripts if one fails

if __name__ == "__main__":
    run_scripts_in_sequence()
