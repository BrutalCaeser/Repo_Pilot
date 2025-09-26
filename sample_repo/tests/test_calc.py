import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calc import add

def test_add_positive():
    assert add(2, 3) == 5
