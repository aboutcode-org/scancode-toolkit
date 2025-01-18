import os
import json
from scancode.plugin_base import FileScanner

def extract_conda_metadata(usr/local/Caskroom/miniforge/base/conda-meta)
    """
    Extracts package-to-file mappings from Conda metadata.
    """
    package_files = {}

    # Iterate through all JSON files in the Conda meta directory
    for json_file in os.listdir(conda_meta_path):
        if json_file.endswith(".json"):
            metadata_file_path = os.path.join(conda_meta_path, json_file)
            with open(metadata_file_path, 'r') as f:
                data = json.load(f)
                package_name = data.get("name")
                package_version = data.get("version")
                files = data.get("files", [])

                # Create a package key and store the data
                package_key = f"{package_name}-{package_version}"
                package_files[package_key] = {
                    "name": package_name,
                    "version": package_version,
                    "type": "conda",
                    "files": files
                }

    return package_files

class CondaPackageScanner(FileScanner):
    """
    A custom scanner to map Conda-installed files to Resources.for_packages.
    """
    def is_enabled(self, **kwargs):
        """
        Enable the scanner only if the Conda meta directory exists.
        """
        conda_meta_path = "/opt/conda/conda-meta"  # Adjust path to your environment
        return os.path.exists(conda_meta_path)

    def scan_file(self, location, resource, **kwargs):
        """
        Scan a resource file and map it to Conda packages if applicable.
        """
        conda_meta_path = "/opt/conda/conda-meta"  # Adjust path to your environment
        if not os.path.exists(conda_meta_path):
            return

        # Extract metadata from Conda
        conda_metadata = extract_conda_metadata(conda_meta_path)

        # Map the resource to Conda packages
        resource.setdefault("for_packages", [])
        for package_key, package_info in conda_metadata.items():
            for installed_file in package_info["files"]:
                if location.endswith(installed_file):
                    package_entry = {
                        "name": package_info["name"],
                        "version": package_info["version"],
                        "type": package_info["type"]
                    }
                    if package_entry not in resource["for_packages"]:
                        resource["for_packages"].append(package_entry)
