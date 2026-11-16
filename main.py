"""
Punto de Entrada Principal (Raíz del Repositorio)
Permite ejecutar el proyecto mediante:
    python main.py
o bien según la especificación formal:
    python -m src.main
"""

import sys
from pathlib import Path

# Añadir raíz al sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.main import main

if __name__ == "__main__":
    main()
