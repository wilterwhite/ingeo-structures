# app/services/analysis/design_behavior.py
"""
Define los comportamientos de diseno para elementos estructurales segun ACI 318-25.

El comportamiento de diseno determina que verificaciones aplicar a un elemento,
independientemente de su tipo Python (Beam, Column, Pier, etc.).

Esto permite que:
- Un Pier clasificado como WALL_PIER_COLUMN reciba verificaciones §18.7 (columna sismica)
- Una Beam con carga axial significativa reciba verificaciones de flexocompresion
- Un DropBeam se disene como muro con diagrama P-M
"""
from enum import Enum, auto


class DesignBehavior(Enum):
    """
    Comportamiento de diseno segun ACI 318-25.

    Cada comportamiento mapea a un conjunto especifico de verificaciones,
    independiente del tipo de entidad Python del elemento.
    """

    # =========================================================================
    # Flexion pura (sin carga axial significativa)
    # =========================================================================
    FLEXURE_ONLY = auto()
    """
    Diseno a flexion pura. ACI 318-25 Capitulo 9.
    Aplica a vigas no-sismicas sin carga axial significativa.
    Verificaciones: Mn >= Mu, refuerzo minimo/maximo, cortante simple.
    """

    # =========================================================================
    # Flexocompresion
    # =========================================================================
    FLEXURE_COMPRESSION = auto()
    """
    Diseno a flexocompresion. ACI 318-25 Capitulo 22.
    Aplica a: columnas no-sismicas, vigas con axial significativo.
    Verificaciones: Diagrama P-M, esbeltez, cortante.
    """

    # =========================================================================
    # Sismico - Capitulo 18
    # =========================================================================
    SEISMIC_BEAM = auto()
    """
    Viga sismica especial. ACI 318-25 §18.6.
    Verificaciones: dimensionales, longitudinales, transversales, cortante Ve.
    """

    SEISMIC_COLUMN = auto()
    """
    Columna sismica especial. ACI 318-25 §18.7.
    Aplica a: columnas sismicas, piers tipo columna (WALL_PIER_COLUMN).
    Verificaciones: columna fuerte-viga debil, confinamiento Ash, cortante Ve.
    """

    SEISMIC_WALL = auto()
    """
    Muro estructural especial. ACI 318-25 §18.10.
    Aplica a: muros esbeltos (hw/lw >= 2.0), muros bajos (squat).
    Verificaciones: cortante amplificado, elementos de borde, cuantias minimas.
    """

    SEISMIC_WALL_PIER_COLUMN = auto()
    """
    Pilar de muro tipo columna. ACI 318-25 §18.10.8.
    Aplica cuando lw/tw <= 2.5 Y hw/lw < 2.0.
    IMPORTANTE: Debe recibir verificaciones §18.7 (columna sismica).
    """

    SEISMIC_WALL_PIER_ALT = auto()
    """
    Pilar de muro alternativo. ACI 318-25 §18.10.8.1.
    Aplica cuando 2.5 < lw/tw <= 6.0.
    Verificaciones especificas de §18.10.8.1.
    """

    # =========================================================================
    # Vigas capitel (Drop beams)
    # =========================================================================
    DROP_BEAM = auto()
    """
    Viga capitel. Se disena como muro con diagrama P-M.
    Verificaciones: flexocompresion, cortante de muro, cuantias.
    """

    SEISMIC_BEAM_COLUMN = auto()
    """
    Viga sismica con carga axial significativa. ACI 318-25 §18.6.4.6.
    Aplica cuando Pu > Ag×f'c/10.
    Verificaciones: usa hoops segun §18.7.5.2-18.7.5.4 (columna).
    Se verifica como columna para requisitos de confinamiento.
    """

    # =========================================================================
    # Strut - Capitulo 23
    # =========================================================================
    STRUT_UNCONFINED = auto()
    """
    Strut no confinado. ACI 318-25 Capitulo 23.
    Aplica a elementos pequenos (<150mm) con 1 barra y sin estribos.
    La barra se considera constructiva - no aporta capacidad.

    Diagrama P-M simplificado:
    - Traccion = 0 (hormigon no armado)
    - Compresion = phi x Fns = 0.75 x 0.34 x fc' x Acs
    - Flexion = Mcr = fr x S (momento de agrietamiento)
    """

    # =========================================================================
    # Propiedades de conveniencia
    # =========================================================================

    @property
    def requires_pm_diagram(self) -> bool:
        """True si requiere diagrama de interaccion P-M."""
        return self in (
            DesignBehavior.FLEXURE_COMPRESSION,
            DesignBehavior.SEISMIC_COLUMN,
            DesignBehavior.SEISMIC_WALL,
            DesignBehavior.SEISMIC_WALL_PIER_COLUMN,
            DesignBehavior.SEISMIC_WALL_PIER_ALT,
            DesignBehavior.DROP_BEAM,
            DesignBehavior.SEISMIC_BEAM_COLUMN,
            DesignBehavior.STRUT_UNCONFINED,  # Diagrama P-M simplificado
        )

    @property
    def requires_seismic_checks(self) -> bool:
        """True si requiere verificaciones sismicas del Capitulo 18."""
        return self in (
            DesignBehavior.SEISMIC_BEAM,
            DesignBehavior.SEISMIC_COLUMN,
            DesignBehavior.SEISMIC_WALL,
            DesignBehavior.SEISMIC_WALL_PIER_COLUMN,
            DesignBehavior.SEISMIC_WALL_PIER_ALT,
            DesignBehavior.SEISMIC_BEAM_COLUMN,
        )

    @property
    def requires_column_checks(self) -> bool:
        """True si requiere verificaciones tipo columna (§18.7)."""
        return self in (
            DesignBehavior.SEISMIC_COLUMN,
            DesignBehavior.SEISMIC_WALL_PIER_COLUMN,
            DesignBehavior.SEISMIC_BEAM_COLUMN,  # §18.6.4.6: hoops segun §18.7.5
        )

    @property
    def requires_wall_checks(self) -> bool:
        """True si requiere verificaciones de muro (§18.10)."""
        return self in (
            DesignBehavior.SEISMIC_WALL,
            DesignBehavior.SEISMIC_WALL_PIER_ALT,
            DesignBehavior.DROP_BEAM,
        )

    @property
    def requires_confinement(self) -> bool:
        """True si requiere verificacion de confinamiento."""
        return self in (
            DesignBehavior.SEISMIC_BEAM,
            DesignBehavior.SEISMIC_COLUMN,
            DesignBehavior.SEISMIC_WALL_PIER_COLUMN,
            DesignBehavior.SEISMIC_BEAM_COLUMN,  # §18.6.4.6
        )

    @property
    def aci_section(self) -> str:
        """Seccion ACI 318-25 principal aplicable."""
        sections = {
            DesignBehavior.FLEXURE_ONLY: "§9",
            DesignBehavior.FLEXURE_COMPRESSION: "§22.4",
            DesignBehavior.SEISMIC_BEAM: "§18.6",
            DesignBehavior.SEISMIC_COLUMN: "§18.7",
            DesignBehavior.SEISMIC_WALL: "§18.10",
            DesignBehavior.SEISMIC_WALL_PIER_COLUMN: "§18.10.8 + §18.7",
            DesignBehavior.SEISMIC_WALL_PIER_ALT: "§18.10.8.1",
            DesignBehavior.DROP_BEAM: "§18.10",
            DesignBehavior.SEISMIC_BEAM_COLUMN: "§18.6.4.6 + §18.7.5",
            DesignBehavior.STRUT_UNCONFINED: "§23.4",
        }
        return sections.get(self, "")

    @property
    def service_type(self) -> str:
        """
        Indica que servicio de dominio usar para verificacion.

        Mapeo:
        - 'column' → SeismicColumnService (§18.7)
        - 'beam' → SeismicBeamService (§18.6)
        - 'wall' → SeismicWallService (§18.10)
        - 'flexure' → FlexocompressionService

        Esto unifica la logica de decision del ElementOrchestrator
        y garantiza consistencia entre comportamiento y servicio.
        """
        mapping = {
            DesignBehavior.FLEXURE_ONLY: "flexure",
            DesignBehavior.FLEXURE_COMPRESSION: "flexure",
            DesignBehavior.SEISMIC_BEAM: "beam",
            DesignBehavior.SEISMIC_COLUMN: "column",
            DesignBehavior.SEISMIC_WALL: "wall",
            DesignBehavior.SEISMIC_WALL_PIER_COLUMN: "column",  # Pier corto usa §18.7
            DesignBehavior.SEISMIC_WALL_PIER_ALT: "wall",
            DesignBehavior.DROP_BEAM: "wall",  # Viga capitel usa §18.10
            DesignBehavior.SEISMIC_BEAM_COLUMN: "column",  # Viga con axial usa §18.7.5
            DesignBehavior.STRUT_UNCONFINED: "strut",  # Strut Cap. 23
        }
        return mapping.get(self, "flexure")
