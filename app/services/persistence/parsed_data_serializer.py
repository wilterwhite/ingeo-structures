# app/services/persistence/parsed_data_serializer.py
"""
Serializador para ParsedData completo.

Permite guardar y restaurar el estado parseado sin re-procesar el Excel.
Esto reduce el tiempo de carga de ~3-5 segundos a ~100-200ms.

Arquitectura unificada:
- VerticalElement: piers y columnas
- HorizontalElement: vigas frame, spandrel y drop_beam
- ElementForces: fuerzas unificadas para todos los elementos
"""
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.parsed_data import ParsedData


def serialize_parsed_data(parsed_data: 'ParsedData') -> Dict[str, Any]:
    """
    Serializa ParsedData completo a diccionario JSON-compatible.

    NO incluye raw_data (DataFrames) para minimizar tamaño.
    """
    return {
        'version': '4.0',  # Version con ElementForces unificado
        'vertical_elements': _serialize_vertical_elements(parsed_data.vertical_elements),
        'vertical_forces': _serialize_forces(parsed_data.vertical_forces),
        'horizontal_elements': _serialize_horizontal_elements(parsed_data.horizontal_elements),
        'horizontal_forces': _serialize_forces(parsed_data.horizontal_forces),
        'materials': parsed_data.materials,
        'stories': parsed_data.stories,
        'continuity_info': _serialize_continuity_info(parsed_data.continuity_info),
        'building_info': _serialize_building_info(parsed_data.building_info),
        'default_coupling_beam': _serialize_coupling_beam(parsed_data.default_coupling_beam),
        'pier_coupling_configs': _serialize_pier_coupling_configs(parsed_data.pier_coupling_configs),
    }


def deserialize_parsed_data(data: Dict[str, Any]) -> 'ParsedData':
    """
    Deserializa diccionario a ParsedData.

    Soporta migración desde versiones anteriores.
    """
    from ...domain.entities.parsed_data import ParsedData

    version = data.get('version', '1.0')

    # Migrar desde versiones anteriores (v2 o v3)
    if version < '4.0':
        return _migrate_from_v2_v3(data)

    return ParsedData(
        vertical_elements=_deserialize_vertical_elements(data.get('vertical_elements', {})),
        vertical_forces=_deserialize_forces(data.get('vertical_forces', {})),
        horizontal_elements=_deserialize_horizontal_elements(data.get('horizontal_elements', {})),
        horizontal_forces=_deserialize_forces(data.get('horizontal_forces', {})),
        materials=data.get('materials', {}),
        stories=data.get('stories', []),
        raw_data={},  # No restauramos raw_data
        continuity_info=_deserialize_continuity_info(data.get('continuity_info')),
        building_info=_deserialize_building_info(data.get('building_info')),
        default_coupling_beam=_deserialize_coupling_beam(data.get('default_coupling_beam')),
        pier_coupling_configs=_deserialize_pier_coupling_configs(data.get('pier_coupling_configs', {})),
    )


# =============================================================================
# MIGRACIÓN DESDE V2/V3
# =============================================================================

def _migrate_from_v2_v3(data: Dict[str, Any]) -> 'ParsedData':
    """Migra datos desde formato v2/v3 a v4 (ElementForces unificado)."""
    from ...domain.entities.parsed_data import ParsedData
    from ...domain.entities import (
        VerticalElement, VerticalElementSource,
        HorizontalElement, HorizontalElementSource,
        DiscreteReinforcement, MeshReinforcement,
        HorizontalDiscreteReinforcement, HorizontalMeshReinforcement,
        ElementForces, ElementForceType,
    )
    from ...domain.entities.load_combination import LoadCombination

    vertical_elements = {}
    vertical_forces = {}
    horizontal_elements = {}
    horizontal_forces = {}

    version = data.get('version', '1.0')

    # =========================================================================
    # Si es v3, los elementos ya están en formato unificado
    # =========================================================================
    if version >= '3.0':
        # Deserializar elementos directamente
        for key, elem_data in data.get('vertical_elements', {}).items():
            vertical_elements[key] = VerticalElement.from_dict(elem_data)

        for key, elem_data in data.get('horizontal_elements', {}).items():
            horizontal_elements[key] = HorizontalElement.from_dict(elem_data)

        # Migrar fuerzas de v3 (todavía separadas por tipo)
        for key, force_data in data.get('vertical_forces', {}).items():
            combinations = [
                LoadCombination(**c) for c in force_data.get('combinations', [])
            ]
            # Detectar tipo por la clave del label
            if 'pier_label' in force_data:
                vertical_forces[key] = ElementForces(
                    label=force_data['pier_label'],
                    story=force_data['story'],
                    element_type=ElementForceType.PIER,
                    combinations=combinations,
                )
            elif 'column_label' in force_data:
                vertical_forces[key] = ElementForces(
                    label=force_data['column_label'],
                    story=force_data['story'],
                    element_type=ElementForceType.COLUMN,
                    combinations=combinations,
                    height=force_data.get('height', 0),
                )
            elif 'label' in force_data:
                # Ya tiene formato nuevo
                elem_type = force_data.get('element_type', 'pier')
                vertical_forces[key] = ElementForces(
                    label=force_data['label'],
                    story=force_data['story'],
                    element_type=ElementForceType(elem_type),
                    combinations=combinations,
                    height=force_data.get('height', 0),
                )

        for key, force_data in data.get('horizontal_forces', {}).items():
            combinations = [
                LoadCombination(**c) for c in force_data.get('combinations', [])
            ]
            if 'beam_label' in force_data:
                # Detectar tipo por key
                if 'drop_beam' in key.lower() or '_DB_' in key or '_Scut' in key:
                    elem_type = ElementForceType.DROP_BEAM
                else:
                    elem_type = ElementForceType.BEAM
                horizontal_forces[key] = ElementForces(
                    label=force_data['beam_label'],
                    story=force_data['story'],
                    element_type=elem_type,
                    combinations=combinations,
                    length=force_data.get('length', 0),
                )
            elif 'label' in force_data:
                # Ya tiene formato nuevo
                elem_type = force_data.get('element_type', 'beam')
                horizontal_forces[key] = ElementForces(
                    label=force_data['label'],
                    story=force_data['story'],
                    element_type=ElementForceType(elem_type),
                    combinations=combinations,
                    length=force_data.get('length', 0),
                )

    else:
        # =====================================================================
        # Migración desde v2 (piers/columns/beams separados)
        # =====================================================================

        # Migrar piers -> VerticalElement (source=PIER)
        for key, pier_data in data.get('piers', {}).items():
            elem = VerticalElement(
                label=pier_data['label'],
                story=pier_data['story'],
                source=VerticalElementSource.PIER,
                length=pier_data['width'],  # lw
                thickness=pier_data['thickness'],  # tw
                height=pier_data['height'],
                fc=pier_data['fc'],
                fy=pier_data.get('fy', 420),
                mesh_reinforcement=MeshReinforcement(
                    n_meshes=pier_data.get('n_meshes', 2),
                    diameter_v=pier_data.get('diameter_v', 8),
                    spacing_v=pier_data.get('spacing_v', 200),
                    diameter_h=pier_data.get('diameter_h', 8),
                    spacing_h=pier_data.get('spacing_h', 200),
                    n_edge_bars=pier_data.get('n_edge_bars', 2),
                    diameter_edge=pier_data.get('diameter_edge', 12),
                ),
                stirrup_diameter=pier_data.get('stirrup_diameter', 10),
                stirrup_spacing=pier_data.get('stirrup_spacing', 150),
                n_shear_legs=pier_data.get('n_stirrup_legs', 2),
                cover=pier_data.get('cover', 25.0),
                axis_angle=pier_data.get('axis_angle', 0.0),
                is_seismic=pier_data.get('is_seismic', True),
                seismic_category=pier_data.get('seismic_category'),
            )
            vertical_elements[key] = elem

        # Migrar pier_forces
        for key, pf_data in data.get('pier_forces', {}).items():
            combinations = [
                LoadCombination(**c) for c in pf_data.get('combinations', [])
            ]
            vertical_forces[key] = ElementForces(
                label=pf_data['pier_label'],
                story=pf_data['story'],
                element_type=ElementForceType.PIER,
                combinations=combinations,
            )

        # Migrar columns -> VerticalElement (source=FRAME)
        for key, col_data in data.get('columns', {}).items():
            elem = VerticalElement(
                label=col_data['label'],
                story=col_data['story'],
                source=VerticalElementSource.FRAME,
                length=col_data['depth'],
                thickness=col_data['width'],
                height=col_data['height'],
                fc=col_data['fc'],
                fy=col_data.get('fy', 420),
                section_name=col_data.get('section_name', ''),
                discrete_reinforcement=DiscreteReinforcement(
                    n_bars_length=col_data.get('n_bars_depth', 3),
                    n_bars_thickness=col_data.get('n_bars_width', 3),
                    diameter=col_data.get('diameter_long', 20),
                ),
                stirrup_diameter=col_data.get('stirrup_diameter', 10),
                stirrup_spacing=col_data.get('stirrup_spacing', 150),
                n_shear_legs=col_data.get('n_stirrup_legs_depth', 2),
                n_shear_legs_secondary=col_data.get('n_stirrup_legs_width', 2),
                cover=col_data.get('cover', 40.0),
                is_seismic=col_data.get('is_seismic', True),
                lu=col_data.get('lu'),
            )
            vertical_elements[key] = elem

        # Migrar column_forces
        for key, cf_data in data.get('column_forces', {}).items():
            combinations = [
                LoadCombination(**c) for c in cf_data.get('combinations', [])
            ]
            vertical_forces[key] = ElementForces(
                label=cf_data['column_label'],
                story=cf_data['story'],
                element_type=ElementForceType.COLUMN,
                combinations=combinations,
                height=cf_data.get('height', 0),
            )

        # Migrar beams -> HorizontalElement
        for key, beam_data in data.get('beams', {}).items():
            source_str = beam_data.get('beam_type', beam_data.get('source', 'frame'))
            source = HorizontalElementSource(source_str.lower())

            elem = HorizontalElement(
                label=beam_data['label'],
                story=beam_data['story'],
                source=source,
                length=beam_data.get('length', 5000),
                depth=beam_data['depth'],
                width=beam_data['width'],
                fc=beam_data['fc'],
                fy=beam_data.get('fy', 420),
                section_name=beam_data.get('section_name', ''),
                discrete_reinforcement=HorizontalDiscreteReinforcement(
                    n_bars_top=beam_data.get('n_bars_top', 3),
                    diameter_top=beam_data.get('diameter_top', 16),
                    n_bars_bottom=beam_data.get('n_bars_bottom', 3),
                    diameter_bottom=beam_data.get('diameter_bottom', 16),
                ) if source != HorizontalElementSource.DROP_BEAM else None,
                stirrup_diameter=beam_data.get('stirrup_diameter', 10),
                stirrup_spacing=beam_data.get('stirrup_spacing', 150),
                n_shear_legs=beam_data.get('n_stirrup_legs', beam_data.get('n_legs', 2)),
                cover=beam_data.get('cover', 40.0),
                ln=beam_data.get('ln'),
            )
            horizontal_elements[key] = elem

        # Migrar beam_forces
        for key, bf_data in data.get('beam_forces', {}).items():
            combinations = [
                LoadCombination(**c) for c in bf_data.get('combinations', [])
            ]
            horizontal_forces[key] = ElementForces(
                label=bf_data['beam_label'],
                story=bf_data['story'],
                element_type=ElementForceType.BEAM,
                combinations=combinations,
                length=bf_data.get('length', 0),
            )

        # Migrar drop_beams -> HorizontalElement (source=DROP_BEAM)
        for key, db_data in data.get('drop_beams', {}).items():
            elem = HorizontalElement(
                label=db_data['label'],
                story=db_data['story'],
                source=HorizontalElementSource.DROP_BEAM,
                length=db_data.get('length', 5000),
                depth=db_data.get('depth', db_data.get('thickness', 290)),
                width=db_data.get('width', 1500),
                fc=db_data['fc'],
                fy=db_data.get('fy', 420),
                mesh_reinforcement=HorizontalMeshReinforcement(
                    n_meshes=db_data.get('n_meshes', 2),
                    diameter_v=db_data.get('diameter_v', 12),
                    spacing_v=db_data.get('spacing_v', 200),
                    diameter_h=db_data.get('diameter_h', 10),
                    spacing_h=db_data.get('spacing_h', 200),
                    n_edge_bars=db_data.get('n_edge_bars', 4),
                    diameter_edge=db_data.get('diameter_edge', 16),
                ),
                stirrup_diameter=db_data.get('stirrup_diameter', 10),
                stirrup_spacing=db_data.get('stirrup_spacing', 150),
                n_shear_legs=db_data.get('n_stirrup_legs', 2),
                cover=db_data.get('cover', 25.0),
                axis_slab=db_data.get('axis_slab', ''),
                location=db_data.get('location', ''),
            )
            horizontal_elements[key] = elem

        # Migrar drop_beam_forces
        for key, dbf_data in data.get('drop_beam_forces', {}).items():
            combinations = [
                LoadCombination(**c) for c in dbf_data.get('combinations', [])
            ]
            horizontal_forces[key] = ElementForces(
                label=dbf_data.get('drop_beam_label', dbf_data.get('beam_label', '')),
                story=dbf_data['story'],
                element_type=ElementForceType.DROP_BEAM,
                combinations=combinations,
            )

    return ParsedData(
        vertical_elements=vertical_elements,
        vertical_forces=vertical_forces,
        horizontal_elements=horizontal_elements,
        horizontal_forces=horizontal_forces,
        materials=data.get('materials', {}),
        stories=data.get('stories', []),
        raw_data={},
        continuity_info=_deserialize_continuity_info(data.get('continuity_info')),
        building_info=_deserialize_building_info(data.get('building_info')),
        default_coupling_beam=_deserialize_coupling_beam(data.get('default_coupling_beam')),
        pier_coupling_configs=_deserialize_pier_coupling_configs(data.get('pier_coupling_configs', {})),
    )


# =============================================================================
# VERTICAL ELEMENTS
# =============================================================================

def _serialize_vertical_elements(elements: Dict[str, Any]) -> Dict[str, Any]:
    """Serializa diccionario de VerticalElement."""
    return {
        key: elem.to_dict()
        for key, elem in elements.items()
    }


def _deserialize_vertical_elements(data: Dict[str, Any]) -> Dict[str, Any]:
    """Deserializa diccionario de VerticalElement."""
    from ...domain.entities import VerticalElement

    return {
        key: VerticalElement.from_dict(elem_data)
        for key, elem_data in data.items()
    }


# =============================================================================
# FORCES (UNIFICADO)
# =============================================================================

def _serialize_forces(forces: Dict[str, Any]) -> Dict[str, Any]:
    """Serializa diccionario de ElementForces."""
    return {
        key: _serialize_force(force)
        for key, force in forces.items()
    }


def _serialize_force(force) -> Dict[str, Any]:
    """Serializa un objeto ElementForces."""
    result = {
        'label': force.label,
        'story': force.story,
        'element_type': force.element_type.value,
        'combinations': [
            {
                'name': c.name,
                'location': c.location,
                'step_type': c.step_type,
                'P': c.P,
                'V2': c.V2,
                'V3': c.V3,
                'T': c.T,
                'M2': c.M2,
                'M3': c.M3,
            }
            for c in force.combinations
        ]
    }

    # Campos opcionales
    if force.height:
        result['height'] = force.height
    if force.length:
        result['length'] = force.length
    if force.section_cut:
        result['section_cut'] = {
            'name': force.section_cut.name,
            'story': force.section_cut.story,
            'thickness_mm': force.section_cut.thickness_mm,
            'width_mm': force.section_cut.width_mm,
            'axis_slab': force.section_cut.axis_slab,
            'location': force.section_cut.location,
        }

    return result


def _deserialize_forces(data: Dict[str, Any]) -> Dict[str, Any]:
    """Deserializa diccionario de ElementForces."""
    from ...domain.entities import ElementForces, ElementForceType
    from ...domain.entities.load_combination import LoadCombination
    from ...domain.entities.section_cut import SectionCutInfo

    result = {}
    for key, force_data in data.items():
        combinations = [
            LoadCombination(**c) for c in force_data.get('combinations', [])
        ]

        # Reconstruir section_cut si existe
        section_cut = None
        if 'section_cut' in force_data:
            sc_data = force_data['section_cut']
            section_cut = SectionCutInfo(
                name=sc_data['name'],
                story=sc_data['story'],
                thickness_mm=sc_data['thickness_mm'],
                width_mm=sc_data['width_mm'],
                axis_slab=sc_data.get('axis_slab', ''),
                location=sc_data.get('location', ''),
            )

        result[key] = ElementForces(
            label=force_data['label'],
            story=force_data['story'],
            element_type=ElementForceType(force_data['element_type']),
            combinations=combinations,
            height=force_data.get('height', 0),
            length=force_data.get('length', 0),
            section_cut=section_cut,
        )

    return result


# =============================================================================
# HORIZONTAL ELEMENTS
# =============================================================================

def _serialize_horizontal_elements(elements: Dict[str, Any]) -> Dict[str, Any]:
    """Serializa diccionario de HorizontalElement."""
    return {
        key: elem.to_dict()
        for key, elem in elements.items()
    }


def _deserialize_horizontal_elements(data: Dict[str, Any]) -> Dict[str, Any]:
    """Deserializa diccionario de HorizontalElement."""
    from ...domain.entities import HorizontalElement

    return {
        key: HorizontalElement.from_dict(elem_data)
        for key, elem_data in data.items()
    }


# =============================================================================
# CONTINUITY INFO
# =============================================================================

def _serialize_continuity_info(continuity_info: Optional[Dict]) -> Optional[Dict[str, Any]]:
    """Serializa diccionario de WallContinuityInfo."""
    if not continuity_info:
        return None

    return {
        key: {
            'pier_key': info.pier_key,
            'label': info.label,
            'story': info.story,
            'is_continuous': info.is_continuous,
            'n_stories': info.n_stories,
            'stories_list': info.stories_list,
            'pier_height': info.pier_height,
            'hwcs': info.hwcs,
            'height_above': info.height_above,
            'height_below': info.height_below,
            'is_base': info.is_base,
            'is_top': info.is_top,
            'story_index': info.story_index,
        }
        for key, info in continuity_info.items()
    }


def _deserialize_continuity_info(data: Optional[Dict]) -> Optional[Dict]:
    """Deserializa diccionario de WallContinuityInfo."""
    if not data:
        return None

    from ...domain.calculations.wall_continuity import WallContinuityInfo

    return {
        key: WallContinuityInfo(
            pier_key=info_data['pier_key'],
            label=info_data['label'],
            story=info_data['story'],
            is_continuous=info_data['is_continuous'],
            n_stories=info_data['n_stories'],
            stories_list=info_data['stories_list'],
            pier_height=info_data['pier_height'],
            hwcs=info_data['hwcs'],
            height_above=info_data['height_above'],
            height_below=info_data['height_below'],
            is_base=info_data['is_base'],
            is_top=info_data['is_top'],
            story_index=info_data['story_index'],
        )
        for key, info_data in data.items()
    }


# =============================================================================
# BUILDING INFO
# =============================================================================

def _serialize_building_info(building_info) -> Optional[Dict[str, Any]]:
    """Serializa BuildingInfo."""
    if not building_info:
        return None

    return {
        'n_stories': building_info.n_stories,
        'stories': building_info.stories,
        'total_height_mm': building_info.total_height_mm,
        'hn_ft': building_info.hn_ft,
        'hn_m': building_info.hn_m,
    }


def _deserialize_building_info(data: Optional[Dict]) -> Optional[Any]:
    """Deserializa BuildingInfo."""
    if not data:
        return None

    from ...domain.calculations.wall_continuity import BuildingInfo

    return BuildingInfo(
        n_stories=data['n_stories'],
        stories=data['stories'],
        total_height_mm=data['total_height_mm'],
        hn_ft=data['hn_ft'],
        hn_m=data['hn_m'],
    )


# =============================================================================
# COUPLING BEAM CONFIG
# =============================================================================

def _serialize_coupling_beam(coupling_beam) -> Optional[Dict[str, Any]]:
    """Serializa CouplingBeamConfig."""
    if not coupling_beam:
        return None

    return {
        'width': coupling_beam.width,
        'height': coupling_beam.height,
        'ln': coupling_beam.ln,
        'n_bars_top': coupling_beam.n_bars_top,
        'diameter_top': coupling_beam.diameter_top,
        'n_bars_bottom': coupling_beam.n_bars_bottom,
        'diameter_bottom': coupling_beam.diameter_bottom,
        'stirrup_diameter': coupling_beam.stirrup_diameter,
        'stirrup_spacing': coupling_beam.stirrup_spacing,
        'n_legs': coupling_beam.n_legs,
        'fy': coupling_beam.fy,
        'fc': coupling_beam.fc,
    }


def _deserialize_coupling_beam(data: Optional[Dict]) -> Optional[Any]:
    """Deserializa CouplingBeamConfig."""
    if not data:
        return None

    from ...domain.entities.coupling_beam import CouplingBeamConfig

    return CouplingBeamConfig(**data)


# =============================================================================
# PIER COUPLING CONFIGS
# =============================================================================

def _serialize_pier_coupling_configs(configs: Dict) -> Dict[str, Any]:
    """Serializa diccionario de PierCouplingConfig."""
    return {
        key: {
            'pier_key': config.pier_key,
            'has_beam_left': config.has_beam_left,
            'has_beam_right': config.has_beam_right,
        }
        for key, config in configs.items()
    }


def _deserialize_pier_coupling_configs(data: Dict) -> Dict:
    """Deserializa diccionario de PierCouplingConfig."""
    if not data:
        return {}

    from ...domain.entities.coupling_beam import PierCouplingConfig

    return {
        key: PierCouplingConfig(
            pier_key=config_data['pier_key'],
            has_beam_left=config_data.get('has_beam_left', True),
            has_beam_right=config_data.get('has_beam_right', True),
        )
        for key, config_data in data.items()
    }
