# Example usage

The directory `project` contains a simple CMake project.

The `script.py` file contains example usage of cmake file api.

Running it should give a output like:
```
$ python3 ./script.py
/usr/bin/python3.7 /home/maarten/programming/python-cmake-file-api/example/script.py
cmake path: /usr/bin/cmake
version: 3.17.2
projects: ['test_project']
targets: ['base', 'dep', 'exe']
target dependencies: {'base': [], 'dep': ['base'], 'exe': ['base', 'dep']}
```
