"""
Configurações para suprimir avisos FontBBox do pdfplumber.
"""

import warnings
import logging

# Suprimir avisos FontBBox
warnings.filterwarnings("ignore", message=".*FontBBox.*")
warnings.filterwarnings("ignore", message=".*cannot be parsed as 4 floats.*")

# Configurar logging para pdfplumber
logging.getLogger("pdfplumber").setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.ERROR)