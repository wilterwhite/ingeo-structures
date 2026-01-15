# app/services/presentation/summary_builder.py
"""
Constructor de resumen para el frontend.

Transforma ParsedData en un formato estructurado para visualización,
separando elementos por tipo y source.
"""
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities import ParsedData


def build_summary_from_parsed_data(parsed_data: 'ParsedData') -> Dict[str, Any]:
    """
    Construye el summary para el frontend desde ParsedData.

    Args:
        parsed_data: Datos parseados del modelo estructural

    Returns:
        Dict con listas de elementos separados por tipo y metadatos
    """
    from ...domain.entities import VerticalElementSource, HorizontalElementSource

    # Separar elementos verticales por source
    piers_list = []
    columns_list = []
    for key, elem in parsed_data.vertical_elements.items():
        item = {
            'key': key,
            'label': elem.label,
            'story': elem.story,
            'width': elem.thickness,  # tw
            'fc': elem.fc,
        }
        if elem.source == VerticalElementSource.PIER:
            item['grilla'] = getattr(elem, 'grilla', '')
            item['eje'] = getattr(elem, 'eje', '')
            item['thickness'] = elem.thickness
            piers_list.append(item)
        else:  # FRAME (column)
            item['section'] = getattr(elem, 'section_name', '')
            item['depth'] = elem.length
            columns_list.append(item)

    # Separar elementos horizontales por source
    beams_list = []
    drop_beams_list = []
    for key, elem in parsed_data.horizontal_elements.items():
        item = {
            'key': key,
            'label': elem.label,
            'story': elem.story,
            'depth': elem.depth,
            'width': elem.width,
            'fc': elem.fc,
        }
        if elem.source == HorizontalElementSource.DROP_BEAM:
            drop_beams_list.append(item)
        else:  # FRAME or SPANDREL
            item['section'] = getattr(elem, 'section_name', '')
            beams_list.append(item)

    # Grillas y ejes solo de piers
    grillas = sorted(set(
        getattr(e, 'grilla', '') for e in parsed_data.vertical_elements.values()
        if e.source == VerticalElementSource.PIER and getattr(e, 'grilla', '')
    ))
    axes = sorted(set(
        getattr(e, 'eje', '') for e in parsed_data.vertical_elements.values()
        if e.source == VerticalElementSource.PIER and getattr(e, 'eje', '')
    ))

    return {
        'total_piers': len(piers_list),
        'total_columns': len(columns_list),
        'total_beams': len(beams_list),
        'total_drop_beams': len(drop_beams_list),
        'piers_list': piers_list,
        'columns_list': columns_list,
        'beams_list': beams_list,
        'drop_beams_list': drop_beams_list,
        'stories': parsed_data.stories,
        'grillas': grillas,
        'axes': axes,
        'materials': parsed_data.materials,
    }
