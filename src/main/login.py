
import os
import sys
# A könyvtár relatív elérési útja
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from auth.auth import *

login()