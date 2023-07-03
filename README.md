# bioio-base

[![Build Status](https://github.com/bioio-devs/bioio-base/workflows/CI/badge.svg)](https://github.com/bioio-devs/bioio-base/actions)
[![Documentation](https://github.com/bioio-devs/bioio-base/workflows/Documentation/badge.svg)](https://bioio-devs.github.io/bioio-base)

Typing, base classes, and more for BioIO projects.

---

## Installation

**Stable Release:** `pip install bioio-base`<br>
**Development Head:** `pip install git+https://github.com/bioio-devs/bioio-base.git`

## Quickstart

```python
from bioio_base.reader import Reader

class CustomTiffReader(Reader):
    # Your code here
```

```python
from typing import List

from bioio_base.reader_metadata import ReaderMetadata as BaseReaderMetadata

class ReaderMetadata(BaseReaderMetadata):
    @staticmethod
    def get_supported_extensions() -> List[str]:
        return ["tif", "tiff"]

    @staticmethod
    def get_reader() -> bioio_base.reader.Reader:
        from .custom_tiff_reader import CustomTiffReader

        return CustomTiffReader
```

## Documentation

For full package documentation please visit [bioio-devs.github.io/bioio-base](https://bioio-devs.github.io/bioio-base).

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

**BSD License**
