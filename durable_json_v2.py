"""Exclusive durable JSON, including creation of every ancestor directory."""
import json
import os
from pathlib import Path


def write_new(path,value):
    path=Path(path)
    raw=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(descriptor,'wb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    # Sync directory contents AND the entries creating new directories in each
    # ancestor. A failure leaves a consumed marker and must precede any launch.
    directory=path.parent.resolve()
    while True:
        descriptor=os.open(directory,os.O_RDONLY)
        try:os.fsync(descriptor)
        finally:os.close(descriptor)
        if directory.parent==directory:break
        directory=directory.parent
