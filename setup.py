from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="contraction-fix",
    version="0.2.2",
    description="A fast and efficient library for fixing contractions in text with reverse functionality and batch processing support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sean Gao",
    author_email="seangaoxy@gmail.com",
    packages=find_packages(),
    package_data={
        "contraction_fix": [
            "data/standard_contractions.json",
            "data/informal_contractions.json",
            "data/internet_slang.json"
        ],
    },
    install_requires=[],
    python_requires=">=3.8",
    license="MIT",
    project_urls={
        "Homepage": "https://github.com/xga0/contraction_fix",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Linguistic",
    ],
) 