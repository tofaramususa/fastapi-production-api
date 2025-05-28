#!/usr/bin/env python3
import json
import sys
import os
import argparse
from typing import Dict, Any, Set, Tuple, List, Optional
from colorama import init, Fore, Style  # For colored terminal output

# Initialize colorama for cross-platform colored terminal output
init()


def extract_structure(json_obj: Any, path: str = "") -> Set[str]:
    """
    Recursively extract the structure of a JSON object, returning a set of paths.
    Each path represents a key or nested key in dot notation.
    """
    paths = set()

    if isinstance(json_obj, dict):
        # If it's an empty dict, still record the path
        if not json_obj:
            paths.add(f"{path} (empty dict)")
        for key, value in json_obj.items():
            current_path = f"{path}.{key}" if path else key
            paths.add(current_path)
            paths.update(extract_structure(value, current_path))
    elif isinstance(json_obj, list):
        # If it's an empty list, still record the path
        if not json_obj:
            paths.add(f"{path} (empty list)")
        elif all(
            isinstance(item, (int, float, str, bool, type(None))) for item in json_obj
        ):
            # If it's a list of primitive values, just record it once
            paths.add(f"{path} (list of {type(json_obj[0]).__name__})")
        else:
            # For lists of complex objects, analyze the first item's structure
            # and note that it's a list
            paths.add(f"{path} (list)")
            paths.update(extract_structure(json_obj[0], f"{path}[item]"))

    return paths


def get_json_from_file_or_input(file_path: Optional[str] = None) -> Any:
    """
    Get JSON data either from a file or request user to paste it in the terminal.
    """
    if file_path:
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Fore.RED}Error: File '{file_path}' not found.{Style.RESET_ALL}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(
                f"{Fore.RED}Error: File '{file_path}' contains invalid JSON.{Style.RESET_ALL}"
            )
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}Error reading {file_path}: {e}{Style.RESET_ALL}")
            sys.exit(1)
    else:
        print(
            f"{Fore.YELLOW}Please paste the JSON data (press Ctrl+D or Ctrl+Z followed by Enter when done):{Style.RESET_ALL}"
        )
        try:
            json_str = sys.stdin.read().strip()
            if not json_str:
                print(f"{Fore.RED}No input provided.{Style.RESET_ALL}")
                sys.exit(1)
            return json.loads(json_str)
        except json.JSONDecodeError:
            print(f"{Fore.RED}Error: Invalid JSON input.{Style.RESET_ALL}")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}Error processing input: {e}{Style.RESET_ALL}")
            sys.exit(1)


def compare_json_structures(json1: Any, json2: Any) -> Tuple[Set[str], Set[str]]:
    """
    Compare the structure of two JSON objects and return the differences.
    """
    # Extract the structure of both JSON objects
    structure1 = extract_structure(json1)
    structure2 = extract_structure(json2)

    # Find keys in json1 that are missing in json2
    missing_in_2 = structure1 - structure2

    # Find keys in json2 that are missing in json1
    missing_in_1 = structure2 - structure1

    return missing_in_1, missing_in_2


def format_missing_keys(missing_keys: Set[str]) -> List[str]:
    """
    Format the set of missing keys for better readability.
    Group by top-level keys and sort.
    """
    if not missing_keys:
        return []

    # Group by top-level key
    grouped = {}
    for path in missing_keys:
        parts = path.split(".")
        top_level = parts[0]
        if top_level not in grouped:
            grouped[top_level] = []
        grouped[top_level].append(path)

    # Format the result
    result = []
    for top_level, paths in sorted(grouped.items()):
        result.append(f"{Fore.CYAN}{top_level}:{Style.RESET_ALL}")
        for path in sorted(paths):
            result.append(f"  - {path}")

    return result


def save_results_to_file(
    missing_in_1: Set[str],
    missing_in_2: Set[str],
    output_file: str,
    file1_name: str,
    file2_name: str,
):
    """
    Save the comparison results to a file.
    """
    with open(output_file, "w") as f:
        if not missing_in_1 and not missing_in_2:
            f.write("The JSON structures match completely.\n")
        else:
            if missing_in_1:
                f.write(f"Keys in {file2_name} missing from {file1_name}:\n")
                for line in format_missing_keys(missing_in_1):
                    # Remove ANSI color codes for file output
                    clean_line = line.replace(Fore.CYAN, "").replace(
                        Style.RESET_ALL, ""
                    )
                    f.write(f"{clean_line}\n")
                f.write("\n")

            if missing_in_2:
                f.write(f"Keys in {file1_name} missing from {file2_name}:\n")
                for line in format_missing_keys(missing_in_2):
                    # Remove ANSI color codes for file output
                    clean_line = line.replace(Fore.CYAN, "").replace(
                        Style.RESET_ALL, ""
                    )
                    f.write(f"{clean_line}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Compare the structure of two JSON files or inputs."
    )
    parser.add_argument(
        "-f1",
        "--file1",
        help="Path to the first JSON file (if omitted, will prompt for input)",
    )
    parser.add_argument(
        "-f2",
        "--file2",
        help="Path to the second JSON file (if omitted, will prompt for input)",
    )
    parser.add_argument(
        "-o", "--output", help="Save the results to this file (optional)"
    )
    parser.add_argument(
        "-d",
        "--detailed",
        action="store_true",
        help="Show detailed structure differences",
    )
    args = parser.parse_args()

    # Get first JSON
    if args.file1:
        print(f"Reading first JSON from file: {args.file1}")
        file1_name = os.path.basename(args.file1)
        json1 = get_json_from_file_or_input(args.file1)
    else:
        print("Enter first JSON:")
        file1_name = "JSON_1"
        json1 = get_json_from_file_or_input()

    # Get second JSON
    if args.file2:
        print(f"Reading second JSON from file: {args.file2}")
        file2_name = os.path.basename(args.file2)
        json2 = get_json_from_file_or_input(args.file2)
    else:
        print("Enter second JSON:")
        file2_name = "JSON_2"
        json2 = get_json_from_file_or_input()

    # Compare the structures
    missing_in_1, missing_in_2 = compare_json_structures(json1, json2)

    # Display the results
    if not missing_in_1 and not missing_in_2:
        print(f"\n{Fore.GREEN}The JSON structures match completely.{Style.RESET_ALL}")
        result_code = 0
    else:
        if missing_in_1:
            print(
                f"\n{Fore.YELLOW}Keys in {file2_name} missing from {file1_name}:{Style.RESET_ALL}"
            )
            for line in format_missing_keys(missing_in_1):
                print(line)

        if missing_in_2:
            print(
                f"\n{Fore.YELLOW}Keys in {file1_name} missing from {file2_name}:{Style.RESET_ALL}"
            )
            for line in format_missing_keys(missing_in_2):
                print(line)
        result_code = 1

    # Save to file if requested
    if args.output:
        save_results_to_file(
            missing_in_1, missing_in_2, args.output, file1_name, file2_name
        )
        print(f"\n{Fore.GREEN}Results saved to {args.output}{Style.RESET_ALL}")

    sys.exit(result_code)


if __name__ == "__main__":
    main()
