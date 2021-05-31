Various scripts that I've written to help make figures in Blender, predominantly involving importing simulation data (from e.g. MuMax).

Note that, for some modules, you need to have `discretisedfield` installed with Blender's version of Python, which handles the loading of magnetization textures from `mumax3`. To do this,
1. Find Blender's python version by opening the Python console within Blender and running
```python
>>> import sys
>>> sys.exec_prefix
```
2. `cd` to the folder containing Blender's Python binary that you just found (you will need to further `cd` to `bin`).
3. Bootstrap `pip` using e.g. `./python3.7m -m ensurepip` (note that the Python version may be different).
4. Run `./python3.7m -m pip install discretisedfield`.