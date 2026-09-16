def deploy(version: str, ready: bool):
    print(f"Deploying version: {version}")

    if not ready:
        print(f"ERROR: Version {version} failed readiness check")
        return False

    print(f"SUCCESS: Version {version} is ready")
    return True


def rollback(previous_version: str):
    print(f"ROLLBACK: Returning to version {previous_version}")
    print(f"SUCCESS: Version {previous_version} restored")


def simulate_bad_release():
    previous_version = "1.0.0"
    new_version = "1.1.0"

    print("=== DEPLOYMENT STARTED ===")

    success = deploy(
        version=new_version,
        ready=False
    )

    if not success:
        rollback(previous_version)

    print("=== DEPLOYMENT FINISHED ===")


if __name__ == "__main__":
    simulate_bad_release()