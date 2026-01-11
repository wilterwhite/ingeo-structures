# app/services/analysis/geometry_normalizer.py
"""
Normalizador de geometria para elementos estructurales.

Centraliza la logica de extraccion de propiedades geometricas de cualquier
tipo de elemento (Column, Pier, Beam, DropBeam) a formatos estandarizados
para los servicios de verificacion.

Usado por ElementOrchestrator para normalizar geometria de cualquier elemento.
"""
import math
from dataclasses import dataclass, field
from typing import Union, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities import Beam, Column, Pier, DropBeam


@dataclass
class ColumnGeometry:
    """
    Geometria normalizada para verificacion tipo columna (ACI 318-25 §18.7).

    Usable para Column, Pier (WALL_PIER_COLUMN) o Beam con axial significativo.
    """
    b: float = 0.0           # Dimension menor (mm)
    h: float = 0.0           # Dimension mayor (mm)
    lu: float = 0.0          # Longitud no arriostrada (mm)
    cover: float = 25.0      # Recubrimiento (mm)
    Ag: float = 0.0          # Area bruta (mm2)
    fc: float = 25.0         # Resistencia del concreto (MPa)
    fy: float = 420.0        # Fluencia del acero longitudinal (MPa)
    fyt: float = 420.0       # Fluencia del acero transversal (MPa)
    Ast: float = 0.0         # Area de acero longitudinal (mm2)
    n_bars: int = 0          # Numero de barras longitudinales
    db_long: float = 16.0    # Diametro barra longitudinal (mm)
    s_transverse: float = 150.0  # Espaciamiento transversal (mm)
    Ash: float = 0.0         # Area de refuerzo transversal (mm2)
    hx: float = 0.0          # Espaciamiento lateral maximo (mm)
    # Momentos para strong-column/weak-beam
    Mnc_top: float = 0.0
    Mnc_bottom: float = 0.0
    Mnb_left: float = 0.0
    Mnb_right: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para paso a servicios."""
        return {
            'b': self.b, 'h': self.h, 'lu': self.lu, 'cover': self.cover,
            'Ag': self.Ag, 'fc': self.fc, 'fy': self.fy, 'fyt': self.fyt,
            'Ast': self.Ast, 'n_bars': self.n_bars, 'db_long': self.db_long,
            's_transverse': self.s_transverse, 'Ash': self.Ash, 'hx': self.hx,
            'Mnc_top': self.Mnc_top, 'Mnc_bottom': self.Mnc_bottom,
            'Mnb_left': self.Mnb_left, 'Mnb_right': self.Mnb_right,
        }


@dataclass
class BeamGeometry:
    """
    Geometria normalizada para verificacion tipo viga (ACI 318-25 §18.6).

    Usable para Beam o Column con axial insignificante.
    """
    bw: float = 0.0          # Ancho del alma (mm)
    h: float = 0.0           # Alto total (mm)
    d: float = 0.0           # Altura efectiva (mm)
    ln: float = 0.0          # Luz libre (mm)
    cover: float = 25.0      # Recubrimiento (mm)
    fc: float = 25.0         # Resistencia del concreto (MPa)
    fy: float = 420.0        # Fluencia del acero longitudinal (MPa)
    fyt: float = 420.0       # Fluencia del acero transversal (MPa)
    As_top: float = 0.0      # Acero superior (mm2)
    As_bottom: float = 0.0   # Acero inferior (mm2)
    n_bars_top: int = 0      # Numero de barras superiores
    n_bars_bottom: int = 0   # Numero de barras inferiores
    db_long: float = 16.0    # Diametro barra longitudinal mayor (mm)
    s_in_zone: float = 150.0   # Espaciamiento en zona plastica (mm)
    s_outside_zone: float = 200.0  # Espaciamiento fuera de zona (mm)
    Av: float = 0.0          # Area transversal (mm2)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para paso a servicios."""
        return {
            'bw': self.bw, 'h': self.h, 'd': self.d, 'ln': self.ln,
            'cover': self.cover, 'fc': self.fc, 'fy': self.fy, 'fyt': self.fyt,
            'As_top': self.As_top, 'As_bottom': self.As_bottom,
            'n_bars_top': self.n_bars_top, 'n_bars_bottom': self.n_bars_bottom,
            'db_long': self.db_long, 's_in_zone': self.s_in_zone,
            's_outside_zone': self.s_outside_zone, 'Av': self.Av,
        }


@dataclass
class WallGeometry:
    """
    Geometria normalizada para verificacion tipo muro (ACI 318-25 §18.10).

    Usable para Pier o DropBeam.
    """
    lw: float = 0.0          # Largo del muro (mm)
    tw: float = 0.0          # Espesor del muro (mm)
    hw: float = 0.0          # Altura del muro (mm)
    cover: float = 25.0      # Recubrimiento (mm)
    Ag: float = 0.0          # Area bruta (mm2)
    Acv: float = 0.0         # Area de corte (mm2)
    fc: float = 25.0         # Resistencia del concreto (MPa)
    fy: float = 420.0        # Fluencia del acero (MPa)
    # Refuerzo distribuido
    rho_v: float = 0.0       # Cuantia vertical
    rho_h: float = 0.0       # Cuantia horizontal
    # Refuerzo de borde
    As_edge: float = 0.0     # Acero de borde total (mm2)
    n_edge_bars: int = 0     # Barras por extremo
    diameter_edge: float = 12.0  # Diametro barras de borde (mm)
    # Confinamiento
    stirrup_diameter: float = 8.0  # Diametro estribos (mm)
    stirrup_spacing: float = 150.0  # Espaciamiento estribos (mm)
    n_stirrup_legs: int = 2  # Numero de ramas

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para paso a servicios."""
        return {
            'lw': self.lw, 'tw': self.tw, 'hw': self.hw, 'cover': self.cover,
            'Ag': self.Ag, 'Acv': self.Acv, 'fc': self.fc, 'fy': self.fy,
            'rho_v': self.rho_v, 'rho_h': self.rho_h,
            'As_edge': self.As_edge, 'n_edge_bars': self.n_edge_bars,
            'diameter_edge': self.diameter_edge,
            'stirrup_diameter': self.stirrup_diameter,
            'stirrup_spacing': self.stirrup_spacing,
            'n_stirrup_legs': self.n_stirrup_legs,
        }


class GeometryNormalizer:
    """
    Normaliza cualquier elemento a geometria estandar.

    Soporta multiples patrones de extraccion para cada tipo de elemento,
    mapeando propiedades a los formatos esperados por los servicios de
    verificacion.

    Uso:
        col_geom = GeometryNormalizer.to_column(element)
        result = column_service.verify(**col_geom.to_dict())

        beam_geom = GeometryNormalizer.to_beam(element)
        result = beam_service.verify(**beam_geom.to_dict())
    """

    @staticmethod
    def to_column(
        element: Union['Column', 'Pier', 'Beam']
    ) -> ColumnGeometry:
        """
        Convierte Column, Pier o Beam a geometria de columna.

        Args:
            element: Elemento a normalizar

        Returns:
            ColumnGeometry con propiedades normalizadas para §18.7
        """
        from ...domain.entities import Column, Pier, Beam

        geom = ColumnGeometry()

        if isinstance(element, Column):
            geom = GeometryNormalizer._column_to_column_geom(element)
        elif isinstance(element, Pier):
            geom = GeometryNormalizer._pier_to_column_geom(element)
        elif isinstance(element, Beam):
            geom = GeometryNormalizer._beam_to_column_geom(element)

        return geom

    @staticmethod
    def to_beam(
        element: Union['Beam', 'Column']
    ) -> BeamGeometry:
        """
        Convierte Beam o Column a geometria de viga.

        Args:
            element: Elemento a normalizar

        Returns:
            BeamGeometry con propiedades normalizadas para §18.6
        """
        from ...domain.entities import Column, Beam

        if isinstance(element, Beam):
            return GeometryNormalizer._beam_to_beam_geom(element)
        elif isinstance(element, Column):
            return GeometryNormalizer._column_to_beam_geom(element)

        return BeamGeometry()

    @staticmethod
    def to_wall(
        element: Union['Pier', 'DropBeam']
    ) -> WallGeometry:
        """
        Convierte Pier o DropBeam a geometria de muro.

        Args:
            element: Elemento a normalizar

        Returns:
            WallGeometry con propiedades normalizadas para §18.10
        """
        from ...domain.entities import Pier, DropBeam

        if isinstance(element, Pier):
            return GeometryNormalizer._pier_to_wall_geom(element)
        elif isinstance(element, DropBeam):
            return GeometryNormalizer._drop_beam_to_wall_geom(element)

        return WallGeometry()

    # =========================================================================
    # CONVERSIONES INTERNAS: TO COLUMN GEOMETRY
    # =========================================================================

    @staticmethod
    def _column_to_column_geom(col: 'Column') -> ColumnGeometry:
        """Extrae geometria de Column para verificacion tipo columna."""
        return ColumnGeometry(
            b=min(col.depth, col.width),
            h=max(col.depth, col.width),
            lu=getattr(col, 'lu_calculated', col.height),
            cover=col.cover,
            Ag=col.Ag,
            fc=col.fc,
            fy=col.fy,
            fyt=col.fy,
            Ast=getattr(col, 'As_longitudinal', 0),
            n_bars=getattr(col, 'n_total_bars', 0),
            db_long=getattr(col, 'diameter_long', 16),
            s_transverse=getattr(col, 'stirrup_spacing', 150),
            Ash=getattr(col, 'Ash_depth', 0),
            hx=getattr(col, 'hx', 0),
            Mnc_top=getattr(col, 'Mnc_top', 0) or 0,
            Mnc_bottom=getattr(col, 'Mnc_bottom', 0) or 0,
            Mnb_left=(getattr(col, 'sum_Mnb_major', 0) or 0) / 2,
            Mnb_right=(getattr(col, 'sum_Mnb_major', 0) or 0) / 2,
        )

    @staticmethod
    def _pier_to_column_geom(pier: 'Pier') -> ColumnGeometry:
        """
        Extrae geometria de Pier para verificacion tipo columna (§18.7).

        Cuando un Pier es clasificado como WALL_PIER_COLUMN (lw/tw <= 2.5, hw/lw < 2.0),
        se trata como columna sismica. La geometria se normaliza:
        - b = min(width, thickness) - dimension menor
        - h = max(width, thickness) - dimension mayor

        Esto permite que el mismo servicio SeismicColumnService verifique
        tanto columnas como wall piers clasificados como columna.
        """
        # Normalizar geometria: b = lado corto, h = lado largo
        b = min(pier.width, pier.thickness)
        h = max(pier.width, pier.thickness)

        # Ash para pier: area de estribo * num ramas
        stirrup_area = math.pi * (pier.stirrup_diameter / 2) ** 2
        Ash = stirrup_area * pier.n_stirrup_legs

        return ColumnGeometry(
            b=b,
            h=h,
            lu=pier.height,
            cover=pier.cover,
            Ag=pier.Ag,
            fc=pier.fc,
            fy=pier.fy,
            fyt=pier.fy,
            # Acero longitudinal: vertical + borde
            Ast=pier.As_vertical + pier.As_edge_total,
            n_bars=pier.n_total_vertical_bars,
            db_long=pier.diameter_v,
            s_transverse=pier.stirrup_spacing,
            Ash=Ash,
            hx=getattr(pier, 'hx', pier.stirrup_spacing),
            # Pier no tiene datos strong-column/weak-beam
            Mnc_top=0,
            Mnc_bottom=0,
            Mnb_left=0,
            Mnb_right=0,
        )

    @staticmethod
    def _beam_to_column_geom(beam: 'Beam') -> ColumnGeometry:
        """Extrae geometria de Beam para verificacion tipo columna."""
        As_top = getattr(beam, 'As_top', 0)
        As_bottom = getattr(beam, 'As_bottom', 0)
        n_top = getattr(beam, 'n_bars_top', 0)
        n_bottom = getattr(beam, 'n_bars_bottom', 0)

        return ColumnGeometry(
            b=beam.width,
            h=beam.depth,
            lu=getattr(beam, 'ln_calculated', beam.length),
            cover=beam.cover,
            Ag=beam.Ag,
            fc=beam.fc,
            fy=beam.fy,
            fyt=beam.fy,
            Ast=As_top + As_bottom,
            n_bars=n_top + n_bottom,
            db_long=max(
                getattr(beam, 'diameter_top', 16),
                getattr(beam, 'diameter_bottom', 16)
            ),
            s_transverse=getattr(beam, 'stirrup_spacing', 150),
            Ash=getattr(beam, 'Av', 0),
            hx=getattr(beam, 'hx', 0),
        )

    # =========================================================================
    # CONVERSIONES INTERNAS: TO BEAM GEOMETRY
    # =========================================================================

    @staticmethod
    def _beam_to_beam_geom(beam: 'Beam') -> BeamGeometry:
        """Extrae geometria de Beam para verificacion tipo viga."""
        return BeamGeometry(
            bw=beam.width,
            h=beam.depth,
            d=beam.d,
            ln=getattr(beam, 'ln_calculated', beam.length),
            cover=beam.cover,
            fc=beam.fc,
            fy=beam.fy,
            fyt=beam.fy,
            As_top=getattr(beam, 'As_top', 0),
            As_bottom=getattr(beam, 'As_bottom', 0),
            n_bars_top=getattr(beam, 'n_bars_top', 0),
            n_bars_bottom=getattr(beam, 'n_bars_bottom', 0),
            db_long=max(
                getattr(beam, 'diameter_top', 16),
                getattr(beam, 'diameter_bottom', 16)
            ),
            s_in_zone=getattr(beam, 'stirrup_spacing', 150),
            s_outside_zone=getattr(beam, 'stirrup_spacing', 200),
            Av=getattr(beam, 'Av', 0),
        )

    @staticmethod
    def _column_to_beam_geom(col: 'Column') -> BeamGeometry:
        """Extrae geometria de Column para verificacion tipo viga."""
        # Columna con axial insignificante tratada como viga
        b = min(col.depth, col.width)
        h = max(col.depth, col.width)
        d = h - col.cover

        return BeamGeometry(
            bw=b,
            h=h,
            d=d,
            ln=getattr(col, 'lu_calculated', col.height),
            cover=col.cover,
            fc=col.fc,
            fy=col.fy,
            fyt=col.fy,
            As_top=getattr(col, 'As_longitudinal', 0) / 2,
            As_bottom=getattr(col, 'As_longitudinal', 0) / 2,
            n_bars_top=getattr(col, 'n_total_bars', 0) // 2,
            n_bars_bottom=getattr(col, 'n_total_bars', 0) // 2,
            db_long=getattr(col, 'diameter_long', 16),
            s_in_zone=getattr(col, 'stirrup_spacing', 150),
            s_outside_zone=getattr(col, 'stirrup_spacing', 150),
            Av=getattr(col, 'Ash_depth', 0),
        )

    # =========================================================================
    # CONVERSIONES INTERNAS: TO WALL GEOMETRY
    # =========================================================================

    @staticmethod
    def _pier_to_wall_geom(pier: 'Pier') -> WallGeometry:
        """Extrae geometria de Pier para verificacion tipo muro."""
        return WallGeometry(
            lw=pier.width,
            tw=pier.thickness,
            hw=pier.height,
            cover=pier.cover,
            Ag=pier.Ag,
            Acv=getattr(pier, 'Acv', pier.width * pier.thickness),
            fc=pier.fc,
            fy=pier.fy,
            rho_v=getattr(pier, 'rho_v', 0),
            rho_h=getattr(pier, 'rho_h', 0),
            As_edge=pier.As_edge_total,
            n_edge_bars=pier.n_edge_bars,
            diameter_edge=pier.diameter_edge,
            stirrup_diameter=pier.stirrup_diameter,
            stirrup_spacing=pier.stirrup_spacing,
            n_stirrup_legs=pier.n_stirrup_legs,
        )

    @staticmethod
    def _drop_beam_to_wall_geom(db: 'DropBeam') -> WallGeometry:
        """Extrae geometria de DropBeam para verificacion tipo muro.

        DropBeam convention:
        - length: luz libre (se usa como lw)
        - thickness: ancho tributario (se usa como tw)
        - width: espesor de la losa
        - height: property que retorna length
        """
        return WallGeometry(
            lw=db.length,        # luz libre
            tw=db.thickness,     # ancho tributario
            hw=db.width,         # espesor de losa (hw para wall)
            cover=getattr(db, 'cover', 25),
            Ag=getattr(db, 'Ag', db.length * db.thickness),
            Acv=getattr(db, 'Acv', db.length * db.thickness),
            fc=db.fc,
            fy=db.fy,
            rho_v=getattr(db, 'rho_vertical', 0),
            rho_h=getattr(db, 'rho_horizontal', 0),
            As_edge=getattr(db, 'As_edge_total', 0),
            n_edge_bars=getattr(db, 'n_edge_bars', 0),
            diameter_edge=getattr(db, 'diameter_edge', 12),
            stirrup_diameter=getattr(db, 'stirrup_diameter', 8),
            stirrup_spacing=getattr(db, 'stirrup_spacing', 150),
            n_stirrup_legs=getattr(db, 'n_stirrup_legs', 2),
        )

    # =========================================================================
    # VALIDACION
    # =========================================================================

    @staticmethod
    def validate_column_geometry(geom: ColumnGeometry) -> list:
        """Valida geometria de columna, retorna lista de warnings."""
        warnings = []
        if geom.b <= 0 or geom.h <= 0:
            warnings.append("Dimensiones invalidas (b o h <= 0)")
        if geom.Ag <= 0:
            warnings.append("Area bruta invalida (Ag <= 0)")
        if geom.Ast <= 0:
            warnings.append("Sin acero longitudinal (Ast <= 0)")
        if geom.s_transverse <= 0:
            warnings.append("Espaciamiento transversal invalido")
        return warnings

    @staticmethod
    def validate_beam_geometry(geom: BeamGeometry) -> list:
        """Valida geometria de viga, retorna lista de warnings."""
        warnings = []
        if geom.bw <= 0 or geom.h <= 0:
            warnings.append("Dimensiones invalidas (bw o h <= 0)")
        if geom.d <= 0:
            warnings.append("Altura efectiva invalida (d <= 0)")
        if geom.As_top <= 0 and geom.As_bottom <= 0:
            warnings.append("Sin acero longitudinal")
        return warnings

    @staticmethod
    def validate_wall_geometry(geom: WallGeometry) -> list:
        """Valida geometria de muro, retorna lista de warnings."""
        warnings = []
        if geom.lw <= 0 or geom.tw <= 0:
            warnings.append("Dimensiones invalidas (lw o tw <= 0)")
        if geom.Ag <= 0:
            warnings.append("Area bruta invalida (Ag <= 0)")
        return warnings
