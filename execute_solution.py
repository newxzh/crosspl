import sys
import json
import traceback


def main():
    try:
        # Read the entire JSON string from stdin.
        json_data = sys.stdin.read()
        data = json.loads(json_data)
        canonical_solution = data['Canonical_solution']

        # Use globals() to simulate the execution environment of the main program.
        exec(canonical_solution, globals())
        print("Execution successful.")
        sys.exit(0)  # Exit successfully.

    except Exception as e:
        # Catch Python exceptions and print to stderr.
        print(f"Execution failed with a Python exception: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)  # Exit with failure.


if __name__ == "__main__":
    main()
