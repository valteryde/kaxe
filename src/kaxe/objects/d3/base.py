"""
Shim so 3D plot objects can be registered via Window.addDrawingFunction.

2D objects implement push/draw for the Pillow pipeline; 3D geometry is added
through render.add3DObject during finalize, so these methods are intentionally empty.
"""

class Base3DObject:

    def push(self, *args, **kwargs):
        pass

    def draw(self, *args, **kwargs):
        pass
