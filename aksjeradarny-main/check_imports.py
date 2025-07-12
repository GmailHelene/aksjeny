import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import pandas as pd
    print(f"Pandas version: {pd.__version__}")
    print("Pandas successfully imported!")
except ImportError as e:
    print(f"Error importing pandas: {e}")

try:
    import numpy as np
    print(f"NumPy version: {np.__version__}")
except ImportError as e:
    print(f"Error importing numpy: {e}")

try:
    import matplotlib.pyplot as plt
    print(f"Matplotlib version: {plt.matplotlib.__version__}")
except ImportError as e:
    print(f"Error importing matplotlib: {e}")

print("\nPython path:")
for path in sys.path:
    print(path)
