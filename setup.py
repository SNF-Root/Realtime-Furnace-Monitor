from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name = "rfs",
    version = "0.1.0",
    packages = find_packages("src"),
    package_dir={"": "src"},
    entry_points = {
        "console_scripts": [
            "rfs = rfs.cli:cli"
        ]
    },
include_package_data=True,
)

