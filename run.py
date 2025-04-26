import subprocess
import sys
import os
import argparse # Import the argparse module

# --- Configuration ---
# Set the correct path to your run.bat file
# You can use an absolute path like r"C:\Users\YourUser\YourProject\run.bat"
# Or a relative path if the script is in the same directory or a known location
# Example: If run.bat is in the same directory as this Python script:
batch_file_path = "run.bat"

# --- Argument Parsing ---
# Create an argument parser for the Python script itself
parser = argparse.ArgumentParser(description="Run a batch file with optional flags.")

# Add the --o argument for the Python script
parser.add_argument(
    '--o',
    action='store_true', # Store True if the flag is present, False otherwise
    help="Pass the --o flag to the batch file."
)

# Add the --spoof argument for the Python script
parser.add_argument(
    '--spoof',
    action='store_true', # Store True if the flag is present, False otherwise
    help="Pass the --spoof flag to the batch file."
)

# Parse the command-line arguments provided to the Python script
args = parser.parse_args()

# --- Execution ---
def run_batch_script(script_path: str, args_to_pass: argparse.Namespace):
    """
    Runs a given batch script using subprocess and passes specified arguments.

    Args:
        script_path: The full or relative path to the batch file (.bat).
        args_to_pass: The argparse Namespace object containing arguments
                      to potentially pass to the batch script.
                      We will pass --o and --spoof if they are True in args_to_pass.

    Returns:
        True if the script ran successfully (exit code 0), False otherwise.
    """
    print(f"Attempting to run batch script: {script_path}")

    # Check if the batch file exists
    if not os.path.exists(script_path):
        print(f"Error: Batch file not found at {script_path}", file=sys.stderr)
        return False

    # Construct the command to pass to the shell
    # Start with the batch file path
    command = f'"{script_path}"' # Enclose path in quotes in case it has spaces

    # Append arguments based on the parsed args from the Python script
    if args_to_pass.o:
        command += " --o" # Add the --o flag if args.o is True
    if args_to_pass.spoof:
        command += " --spoof" # Add the --spoof flag if args.spoof is True

    print(f"Full command to execute: {command}")

    try:
        # Use subprocess.run to execute the command string via the shell
        # shell=True is necessary to execute the command string as a whole,
        # including the batch file path and arguments.
        # capture_output=True captures stdout and stderr
        # text=True decodes stdout and stderr as text using default encoding
        # check=True will raise CalledProcessError if the command returns a non-zero exit code
        result = subprocess.run(
            command, # Pass the full command string
            shell=True,
            capture_output=True,
            text=True,
            check=True # This will raise an exception on non-zero exit code
        )

        # If check=True didn't raise an exception, the script ran successfully
        print("Batch script executed successfully.")

        # Print standard output if any
        if result.stdout:
            print("\n--- Standard Output ---")
            print(result.stdout)

        return True

    except FileNotFoundError:
        # This specific error might occur if 'cmd.exe' (the shell) is not found,
        # which is very unlikely on Windows.
        print(f"Error: The command shell was not found.", file=sys.stderr)
        return False
    except subprocess.CalledProcessError as e:
        # This exception is raised because check=True is set, and the batch file
        # exited with a non-zero status (indicating an error within the batch script)
        print(f"Error: Batch script failed with exit code {e.returncode}", file=sys.stderr)
        print(f"Command: {e.cmd}", file=sys.stderr)

        # Print standard output and error from the failed process
        if e.stdout:
            print("\n--- Standard Output (from error) ---", file=sys.stderr)
            print(e.stdout, file=sys.stderr)
        if e.stderr:
            print("\n--- Standard Error (from error) ---", file=sys.stderr)
            print(e.stderr, file=sys.stderr)

        return False
    except Exception as e:
        # Catch any other unexpected errors during execution
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        # import traceback
        # print(traceback.format_exc(), file=sys.stderr) # Uncomment for full traceback
        return False

# --- Main Execution ---
if __name__ == "__main__":
    # You can now access the parsed arguments provided to the Python script via the 'args' object
    print(f"Parsed arguments for Python script: {args}")
    print(f"Argument 'o' for Python script is set: {args.o}")
    print(f"Argument 'spoof' for Python script is set: {args.spoof}")

    # Call the function to run the batch script and pass the parsed arguments
    success = run_batch_script(batch_file_path, args)

    if success:
        print("\nScript finished successfully.")
    else:
        print("\nScript finished with errors.")
        sys.exit(1) # Exit with a non-zero code to indicate failure

    # Add a line to pause the terminal if needed after execution
    # print("\nPress Enter to exit.")
    # input()
