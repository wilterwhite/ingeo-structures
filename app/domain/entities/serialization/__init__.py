# app/domain/entities/serialization/__init__.py
"""
Módulo de serialización para entidades del dominio.

Centraliza funciones de parsing comunes para evitar duplicación.
"""
from .load_combination import parse_load_combination, LoadCombination

__all__ = ['parse_load_combination', 'LoadCombination']
