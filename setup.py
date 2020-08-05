from setuptools import find_packages, setup


with open("README.md", "r") as fh:
    long_description = fh.read()

packages = find_packages(exclude=("tests", "tests.*", "*.tests"))

setup(
    name="cmake-file-api",
    version="0.0.1",
    license="MIT",
    packages=packages,
    author="Anonymous Maarten",
    author_email="anonymous.maarten@gmail.com",
    description="Read and interpret CMake's file-based API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/madebr/python-cmake-file-api",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "Programming Language :: C",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
)
