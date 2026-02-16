from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sonarr-calendar",
    version="3.0.2",
    author="Your Name",
    description="Sonarr Calendar Tracker - HTML dashboard generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KBW1963/sonarr_calendar",
    package_dir={"": "src"},                # look for packages in src/
    packages=find_packages(where="src"),    # find all packages under src/
    include_package_data=True,
    package_data={
        "sonarr_calendar": ["templates/*.html"],   # include template files
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