import bpy

# Global dictionary for tracking class registrations
registered_classes = set()

def register_class(cls):
    # Unregister class if already registered
    if cls.__name__ in registered_classes:
        bpy.utils.unregister_class(cls)
        registered_classes.remove(cls.__name__)
    # Register class
    bpy.utils.register_class(cls)
    registered_classes.add(cls.__name__)

def unregister_class(cls):
    # Check if the class has been registered before unregistering it
    if cls.__name__ in registered_classes:
        bpy.utils.unregister_class(cls)
        registered_classes.remove(cls.__name__)