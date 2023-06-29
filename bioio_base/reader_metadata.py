#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import List

from .reader import Reader

###############################################################################


class ReaderMetadata(ABC):
    @staticmethod
    @abstractmethod
    def get_supported_extensions() -> List[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_reader() -> Reader:
        pass
