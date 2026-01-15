# app/services/presentation/__init__.py
"""
Servicios de presentación y visualización.
"""
from .plot_generator import PlotGenerator
from .result_formatter import ResultFormatter

__all__ = ['PlotGenerator', 'ResultFormatter']

# ElementDetailsService se importa directamente desde modal_data_service
# para evitar import circular con analysis/
