# Shelf Made
A quick and dirty script shelf for Blender.

![Shelf Made](/docs/images/example.png)

## Warning
This add-on may run any Python script within a given folder without any checks.
Use at your own risk.

> Please thoroughly analyze any script before adding it to your directory.

## Quick Start
1. Install the add-on.
1. Open the 3D view side panel.
1. Click `Add Shelf`.
1. Navigate to a directory containing Python scripts.
1. **Run your *shelf made* scripts in any file!**

## Other Features
* Rename & re-order your shelves & scripts, set icons for them.
* Set column counts & button sizes of your shelves.
* Choose which shelf is visible in which editor.
* Run any other text datablock (ending in `.py`) from the *Local Scripts* panel.
* Edit your scripts directly in the Blender text editor.
* Save any text directly to one of your shelves from the text editor.
* Run adjusted local copies from the *Local Scripts* panel.
* Save edited scripts back to their source.

## Structure
|Module|Description|
|--|--|
|`__init__.py`|Add-on initialization|
|`catalogue.py`|Decorator & class for handling automated bpy class registration|
|`draw.py`|All draw functions for panels|
|`ops.py`|Multitude of operators to set up, organize and customize shelves and scripts|
|`panels.py`|Panel classes: *Local Shelves*, as well as base *Shelves* and their space-based children|
|`preferences.py`|Add-on root class holding settings and shelf objects|
|`shelf.py`|*Shelf* & *Script* class definitions|
|`utils.py`|Additional utilities, mostly UI goodies|
