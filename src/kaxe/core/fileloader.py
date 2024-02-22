
import pkgutil
import io
import os

def loadFile(fname:str) -> io.BytesIO:
    return io.BytesIO(pkgutil.get_data('kaxe', os.path.join('resources', fname)))