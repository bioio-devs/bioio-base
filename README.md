# bioio-types

[![Build Status](https://github.com/bioio-devs/bioio-types/workflows/CI/badge.svg)](https://github.com/bioio-devs/bioio-types/actions)
[![Documentation](https://github.com/bioio-devs/bioio-types/workflows/Documentation/badge.svg)](https://bioio-devs.github.io/bioio-types)

Typing, base classes, and more for BioIO projects.

---

## Installation

**Stable Release:** `pip install bioio-types`<br>
**Development Head:** `pip install git+https://github.com/bioio-devs/bioio-types.git`

## Quickstart

```python
from bioio_types.reader import Reader

class CustomTiffReader(Reader):
    # Your code here
```

```python
from typing import List

from bioio_types.reader_metadata import ReaderMetadata as BaseReaderMetadata

class ReaderMetadata(BaseReaderMetadata):
    @staticmethod
    def get_supported_extensions() -> List[str]:
        return ["tif", "tiff"]

    @staticmethod
    def get_reader() -> base_image_reader.reader.Reader:
        from .custom_tiff_reader import CustomTiffReader

        return CustomTiffReader
```

## Documentation

For full package documentation please visit [bioio-devs.github.io/bioio-types](https://bioio-devs.github.io/bioio-types).

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

**BSD License**
