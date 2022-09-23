# Shelf Made
A quick and dirty script shelf for Blender.

## Warning
This add-on may run any Python script within a given folder without any checks.
Use at your own risk.

> Please thoroughly analyze any script before adding it to your directory.

## Instructions
1. Install the add-on.
1. Open the 3D view side panel.
1. Set your script directory.
1. Open the folder and add some python scripts ending in `.py`.
1. Hit refresh.
1. **Run your *shelf made* scripts in any file!**

## Other Features
* Run any other text datablock (ending in `.py`) from the *Local Scripts* panel.
* Activate *Show Edit Buttons* and edit scripts directly in the Blender text editor.
* Run adjusted local copies from the *Local Scripts* panel.
* Save edited scripts back to their source.

## Structure
|Module|Description|
|--|--|
|`__init__.py`|Add-on initialization|
|`catalogue.py`|Decorator & class for handling automated bpy class registration|
|`draw.py`|All draw functions for panels|
|`ops.py`|Operators: *Execute*, *Refresh*, *Edit*|
|`panels.py`|Panel classes: *Scripts Directory*, *Scripts*, *Local Scripts*|
|`preferences.py`|Add-on root class holding settings and snippet objects|
|`snippet.py`|Snippet class definition with methods to handle single scripts|
|`utils.py`|Additional utilities, mostly UI goodies|

## To Do
* Panels in more areas (script `context` is currently limited to View3D)
* (Custom) icon selection
* Edit display name
* Re-order
* Handle recursive folder structure
* Framework to detect operators and register them directly

## Contribution
Contributions are welcome!

### Requirements
* *Black Formatter*
* Strict typing
* MD compatible docstrings
* Create a pull request
