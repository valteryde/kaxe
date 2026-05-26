
"""
handles compatibility with kaxe.objects
"""

class Base3DObject:

    def push(self, *args, **kwargs):
        # has no effect on 3d objcet
        pass

    
    def draw(self, *args, **kwargs):
        # has no effect on 3d objcet
        pass
