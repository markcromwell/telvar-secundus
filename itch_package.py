#!/usr/bin/env python3
"""
Packages a Godot HTML5 build for itch.io.

This script takes a build directory, creates a timestamped folder,
and zips the contents for uploading to itch.io.
"""
import argparse
import os
import sys
import zipfile
from datetime import datetime

def main():
    """Main function to package the build."""
    parser = argparse.ArgumentParser(description="Package Godot HTML5 build for itch.io.")
    parser.add_argument(
        "--source-dir",
        default="./build",
        help="Path to the source build directory (default: ./build)"
    )
    parser.add_argument(
        "--output-path",
        default="./itch-build.zip",
        help="Path to the output zip file (default: ./itch-build.zip)"
    )
    args = parser.parse_args()

    source_dir = args.source_dir
    output_path = args.output_path

    if not os.path.isdir(source_dir):
        print(f"FAIL: Source directory not found at '{source_dir}'")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    timestamped_folder = f"telvar-{timestamp}"

    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_path = os.path.join(
                        timestamped_folder,
                        os.path.relpath(file_path, source_dir)
                    )
                    zf.write(file_path, archive_path)
        
        print(f"Successfully created '{output_path}' with contents in '{timestamped_folder}/'")

    except Exception as e:
        print(f"FAIL: An error occurred during zip creation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
