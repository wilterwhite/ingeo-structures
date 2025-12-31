# app/services/report/report_config.py
"""
Configuracion para generacion de informes PDF.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class ReportConfig:
    """
    Configuracion del informe PDF.

    Attributes:
        project_name: Nombre del proyecto
        top_by_load: Cantidad de piers a mostrar ordenados por carga
        top_by_cuantia: Cantidad de piers a mostrar ordenados por cuantia
        include_failing: Incluir seccion de piers que fallan
        include_proposals: Incluir propuestas de diseno
        include_pm_diagrams: Incluir diagramas P-M
        include_sections: Incluir secciones transversales
        include_full_table: Incluir tabla completa de resultados
    """
    project_name: str = "Proyecto Sin Nombre"
    top_by_load: int = 5
    top_by_cuantia: int = 5
    include_failing: bool = True
    include_proposals: bool = True
    include_pm_diagrams: bool = True
    include_sections: bool = True
    include_full_table: bool = True

    # Metadata generada automaticamente
    generated_at: Optional[datetime] = field(default=None)

    def __post_init__(self):
        """Inicializa campos automaticos."""
        if self.generated_at is None:
            self.generated_at = datetime.now()

    def validate(self, total_piers: int) -> List[str]:
        """
        Valida la configuracion.

        Args:
            total_piers: Cantidad total de piers disponibles

        Returns:
            Lista de mensajes de error (vacia si todo es valido)
        """
        errors = []

        if self.top_by_load < 0:
            errors.append("Top por carga no puede ser negativo")
        elif self.top_by_load > total_piers:
            errors.append(
                f"Top por carga ({self.top_by_load}) excede "
                f"el total de piers ({total_piers})"
            )

        if self.top_by_cuantia < 0:
            errors.append("Top por cuantia no puede ser negativo")
        elif self.top_by_cuantia > total_piers:
            errors.append(
                f"Top por cuantia ({self.top_by_cuantia}) excede "
                f"el total de piers ({total_piers})"
            )

        if len(self.project_name) > 100:
            errors.append("Nombre del proyecto no puede exceder 100 caracteres")

        return errors

    @classmethod
    def from_dict(cls, data: dict) -> 'ReportConfig':
        """
        Crea una configuracion desde un diccionario.

        Args:
            data: Diccionario con los parametros

        Returns:
            Instancia de ReportConfig
        """
        return cls(
            project_name=data.get('project_name', 'Proyecto Sin Nombre'),
            top_by_load=int(data.get('top_by_load', 5)),
            top_by_cuantia=int(data.get('top_by_cuantia', 5)),
            include_failing=bool(data.get('include_failing', True)),
            include_proposals=bool(data.get('include_proposals', True)),
            include_pm_diagrams=bool(data.get('include_pm_diagrams', True)),
            include_sections=bool(data.get('include_sections', True)),
            include_full_table=bool(data.get('include_full_table', True))
        )

    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            'project_name': self.project_name,
            'top_by_load': self.top_by_load,
            'top_by_cuantia': self.top_by_cuantia,
            'include_failing': self.include_failing,
            'include_proposals': self.include_proposals,
            'include_pm_diagrams': self.include_pm_diagrams,
            'include_sections': self.include_sections,
            'include_full_table': self.include_full_table,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }
