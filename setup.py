from setuptools import setup

from mypyc.build import mypycify

setup(
    use_scm_version=True,
    ext_modules=mypycify(paths=['cmake_file_api/'], verbose=True),
)
