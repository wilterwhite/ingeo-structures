# app/services/report/__init__.py
"""
Modulo de generacion de informes PDF.

Proporciona funcionalidad para generar informes PDF con resultados
de verificacion estructural segun ACI 318-25.
"""

from .report_config import ReportConfig
from .pdf_generator import PDFReportGenerator

__all__ = ['ReportConfig', 'PDFReportGenerator']
