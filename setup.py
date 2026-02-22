import re
from setuptools import setup, find_packages

def get_version():
    """Read the version from src/sonarr_calendar/__init__.py."""
    version_file = "src/sonarr_calendar/__init__.py"
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", content)
        if match:
            return match.group(1)
        raise RuntimeError(f"Unable to find version string in {version_file}")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sonarr-calendar",
    version=get_version(),
    author="Your Name",
    description="Sonarr Calendar Tracker - HTML dashboard generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/sonarr-calendar",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "sonarr_calendar": ["templates/*.html"],
    },
    install_requires=[
        "requests>=2.28.0",
        "jinja2>=3.1.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "sonarr-calendar=sonarr_calendar.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)