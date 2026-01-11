# app/services/presentation/__init__.py
"""
Servicios de presentación y visualización.
"""
from .plot_generator import PlotGenerator
from .result_formatter import ResultFormatter

# Re-export desde nueva ubicación para compatibilidad hacia atrás
# PierDetailsService se movió a services/analysis/ (ya no es un formatter)
from ..analysis.pier_details_service import PierDetailsService, PierDetailsFormatter

__all__ = ['PlotGenerator', 'ResultFormatter', 'PierDetailsService', 'PierDetailsFormatter']
