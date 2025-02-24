def get_version() -> str:
    """
    Returns the current version of the application.

    This function reads the version information from a file named 'version.txt'
    located in the same directory as the script. The file should contain a single
    line with the version number in the format 'x.y.z'.

    Returns:
        str: The version number as a string in the format 'x.y.z'.

    Raises:
        FileNotFoundError: If the 'version.txt' file is not found.
        IOError: If there's an error reading the file.
        ValueError: If the version number in the file is not in the correct format.

    Example:
        >>> get_version()
        '1.2.3'
    """
    try:
        with open('.package-version', 'r') as f:
            version = f.read().strip()

        parts = version.split('.')
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise ValueError("Invalid version format")

        return version
    except FileNotFoundError:
        raise FileNotFoundError("Version file not found")
    except IOError:
        raise IOError("Error reading version file")
