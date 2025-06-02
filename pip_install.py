import subprocess

if __name__ == "__main__":
    subprocess.run(["cd JAVA_project && python3.12 -m venv .venv"], shell=True)

    subprocess.run(
        ["source JAVA_project/.venv/bin/activate && pip install -r requirements.txt"],
        shell=True,
    )
