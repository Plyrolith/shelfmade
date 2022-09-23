from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bpy.types import Context

from pathlib import Path

from bpy.props import BoolProperty, CollectionProperty, StringProperty
from bpy.types import AddonPreferences

from . import catalogue, script


########################################################################################
# Update functions
########################################################################################


def update_script_directory(preferences: Preferences, context: Context):
    """
    Re-scans scripts on directory change.

    Parameters:
        - preferences (Preferences)
        - context (Context)
    """
    preferences.initialize_scripts()


########################################################################################
# Add-on root
########################################################################################


@catalogue.bpy_register
class Preferences(AddonPreferences):
    """Add-on preferences"""

    bl_idname = __package__

    script_directory: StringProperty(
        name="Script Directory",
        subtype="DIR_PATH",
        update=update_script_directory,
    )
    scripts: CollectionProperty(type=script.Script, name="Scripts")
    show_edit_buttons: BoolProperty(name="Show Edit Buttons")

    this: Preferences

    def draw(self, context: Context):
        """
        Draw add-on the preferences panel.

        Parameters:
            - context (Context)
        """
        layout = self.layout
        layout.use_property_split = True

        # Script directory
        layout.prop(data=self, property="script_directory")

        # Show edit buttons
        layout.prop(data=self, property="show_edit_buttons")

    def initialize_scripts(self):
        """
        Scan the script directory and initiate a script object for each script found.
        """
        # Clear scripts
        self.scripts.clear()

        # Check directory
        if not self.script_directory:
            print("Please define a script directory")
            return

        directory = Path(self.script_directory)
        if not directory.is_dir():
            print("Invalid script directory")
            return

        # Iterate directory and find python scripts
        for script_file in directory.iterdir():
            if not script_file.suffix == ".py":
                continue

            # Create a snippet
            script = self.scripts.add()
            script.name = script_file.stem
            script.filepath = str(script_file)
