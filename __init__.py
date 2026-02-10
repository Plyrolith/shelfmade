import bpy
from . import (
    catalog,
    draw,
    ops,
    panels,
    shelf,
    preferences,
)


def register():
    """
    Main registration.
    """
    # Classes registration
    catalog.register()

    # Initialize shelves
    prefs = preferences.Preferences.this()
    prefs.initialize_shelves()

    # Remove nonexistent shelves & scripts
    prefs.clean()

    # Add shelf menu to text editor
    bpy.types.TEXT_HT_header.append(draw.text_editor_shelf_menu)


def unregister():
    """
    De-registration.
    """
    # Remove text editor draw function
    bpy.types.TEXT_HT_header.remove(draw.text_editor_shelf_menu)

    # Classes un-registration
    catalog.unregister()
