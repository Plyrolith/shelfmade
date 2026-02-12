from . import catalog, draw, ops, panels, preferences, shelf  # noqa: E402 F401


def register():
    """
    Main registration.
    """
    catalog.register()


def unregister():
    """
    De-registration.
    """
    catalog.unregister()
