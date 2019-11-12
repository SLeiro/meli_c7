import numpy as np
from enum import Enum


NORTH = np.array(['BR-AC', 'BR-AP', 'BR-AM', 'BR-PA', 'BR-RO', 'BR-RR',
                  'BR-TO', 'BR-AL', 'BR-BA', 'BR-CE', 'BR-MA', 'BR-PB',
                  'BR-PE', 'BR-PI', 'BR-RN', 'BR-SE'])
CENTER = np.array(['BR-ES', 'BR-MG', 'BR-RJ', 'BR-SP', 'BR-GO', 'BR-MT',
                   'BR-MS', 'BR-DF', 'BR-PR'])
SOUTH = np.array(['BR-RS', 'BR-SC'])


class Region(Enum):
    SOUTH = 'south'
    NORTH = 'north'

    @classmethod
    def from_state(cls, state):
        return cls.SOUTH if state in SOUTH else cls.NORTH
