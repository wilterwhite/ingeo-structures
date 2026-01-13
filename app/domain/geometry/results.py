# app/domain/geometry/results.py
"""
Resultados de verificación de geometría ACI 318-25.

Proporciona una estructura unificada para todos los checks de geometría.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class GeometryCheckResult:
    """
    Resultado unificado de verificación de geometría.

    Usado para columnas (§18.7.2), vigas (§18.6.2) y elementos de borde (§18.10.6.4).

    Attributes:
        is_ok: True si todas las verificaciones pasan
        warnings: Lista de advertencias para mostrar en UI
        checks: Dict con resultado de cada verificación individual
        values: Dict con valores calculados/medidos
        aci_reference: Sección ACI aplicable
    """
    is_ok: bool
    warnings: List[str] = field(default_factory=list)
    checks: Dict[str, bool] = field(default_factory=dict)
    values: Dict[str, float] = field(default_factory=dict)
    aci_reference: str = ""

    def add_warning(self, warning: str) -> None:
        """Agrega una advertencia."""
        self.warnings.append(warning)

    def set_check(self, name: str, passed: bool) -> None:
        """Registra el resultado de una verificación."""
        self.checks[name] = passed
        if not passed:
            self.is_ok = False

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'is_ok': self.is_ok,
            'warnings': self.warnings,
            'checks': self.checks,
            'values': self.values,
            'aci_reference': self.aci_reference
        }
