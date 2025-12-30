# scripts/generate_test_data.py
"""
Script para generar datos de prueba para el módulo estructural.
Crea un Excel sintético con piers y combinaciones de carga acotadas.
"""
import os
import sys

# Agregar el path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from io import BytesIO


def generate_test_excel() -> bytes:
    """
    Genera un archivo Excel de prueba con formato ETABS.

    Casos de prueba organizados por categoría:

    GRUPO A - Casos sobrecargados (NO OK esperado):
    - A1: 20x20 cm columna cuadrada, alta carga
    - A2: 20x50 cm, alta carga

    GRUPO B - Casos límite de clasificación:
    - B1: 20x80 cm (lw/tw=4.0 límite columna/muro)
    - B2: 20x120 cm muro con hw/lw=2.5 (esbelto)
    - B3: 25x125 cm muro con hw/lw=2.0 (límite esbelto/achaparrado)

    GRUPO C - Wall piers (§18.10.8):
    - C1: 30x100 cm (lw/tw=3.3, hw/lw<2 → wall pier column)
    - C2: 20x100 cm (lw/tw=5.0, hw/lw<2 → wall pier wall)

    GRUPO D - Cargas ligeras (OK esperado):
    - D1: 30x150 cm muro con cargas bajas
    - D2: 25x200 cm muro achaparrado con cargas bajas

    GRUPO E - Casos especiales de carga:
    - E1: 20x100 cm alta tracción/bajo momento
    - E2: 20x100 cm alto momento/baja compresión

    2 combinaciones de carga por pier.
    """

    # =========================================================================
    # Tabla 1: Pier Section Properties
    # =========================================================================
    pier_props_data = []

    # Definir alturas de piso para controlar hw/lw
    # Piso 1: 3.0m, Piso 2: 3.0m, Piso 3: 2.5m
    piers_config = [
        # (label, story, thickness_m, width_m, material, height_m)
        # GRUPO A - Sobrecargados
        ("A1-Overload", "Piso 1", 0.20, 0.20, "H30", 3.0),   # 20x20 columna
        ("A2-Overload", "Piso 1", 0.20, 0.50, "H30", 3.0),   # 20x50
        # GRUPO B - Límites de clasificación
        ("B1-Limit-4", "Piso 1", 0.20, 0.80, "H30", 3.0),    # lw/tw=4.0 exacto
        ("B2-Slender", "Piso 2", 0.20, 1.20, "H30", 3.0),    # hw/lw=2.5 esbelto
        ("B3-Limit-2", "Piso 3", 0.25, 1.25, "H30", 2.5),    # hw/lw=2.0 exacto
        # GRUPO C - Wall piers
        ("C1-WPColumn", "Piso 1", 0.30, 1.00, "H30", 1.8),   # lw/tw=3.3, hw/lw=1.8
        ("C2-WPWall", "Piso 1", 0.20, 1.00, "H30", 1.5),     # lw/tw=5.0, hw/lw=1.5
        # GRUPO D - Cargas ligeras
        ("D1-LightLoad", "Piso 2", 0.30, 1.50, "H30", 3.0),  # muro con carga baja
        ("D2-SquatOK", "Piso 2", 0.25, 2.00, "H30", 3.0),    # achaparrado hw/lw=1.5
        # GRUPO E - Casos especiales
        ("E1-Tension", "Piso 1", 0.20, 1.00, "H30", 3.0),    # tracción
        ("E2-HighM", "Piso 1", 0.20, 1.00, "H30", 3.0),      # alto momento
    ]

    # Calcular alturas Z acumuladas por piso
    story_heights = {"Piso 1": (0.0, 3.0), "Piso 2": (3.0, 6.0), "Piso 3": (6.0, 8.5)}

    for label, story, thickness, width, material, height in piers_config:
        z_bottom, z_top = story_heights.get(story, (0.0, 3.0))
        # Ajustar z_top si la altura del pier es diferente
        z_top = z_bottom + height

        pier_props_data.append({
            "Story": story,
            "Pier": label,
            "Width Bottom": width,
            "Thickness Bottom": thickness,
            "Width Top": width,
            "Thickness Top": thickness,
            "Material": material,
            "CG Bottom X": 0.0,
            "CG Bottom Y": 0.0,
            "CG Bottom Z": z_bottom,
            "CG Top X": 0.0,
            "CG Top Y": 0.0,
            "CG Top Z": z_top,
        })

    df_pier_props = pd.DataFrame(pier_props_data)

    # =========================================================================
    # Tabla 2: Pier Forces (2 combinaciones por pier)
    # =========================================================================
    pier_forces_data = []

    # Combinaciones de carga
    combos = [
        ("1.4D", "Max"),
        ("1.2D+1.6L", "Max"),
    ]

    # Fuerzas sintéticas para cada pier
    # P negativo = compresión en ETABS
    # Formato: (P, V2, V3, M2, M3) para cada combinación
    forces_config = {
        # GRUPO A - Sobrecargados (deben fallar)
        "A1-Overload": [
            (-50.0, 2.0, 1.5, 0.5, 3.0),      # 1.4D
            (-80.0, 5.0, 3.0, 1.0, 8.0),      # 1.2D+1.6L - alta carga
        ],
        "A2-Overload": [
            (-100.0, 8.0, 2.0, 1.0, 15.0),
            (-150.0, 15.0, 4.0, 2.0, 25.0),
        ],
        # GRUPO B - Límites de clasificación (cargas moderadas)
        "B1-Limit-4": [
            (-40.0, 4.0, 1.0, 0.5, 5.0),      # lw/tw=4.0 límite
            (-60.0, 6.0, 1.5, 0.8, 8.0),
        ],
        "B2-Slender": [
            (-50.0, 5.0, 1.5, 1.0, 10.0),     # muro esbelto
            (-75.0, 8.0, 2.0, 1.5, 15.0),
        ],
        "B3-Limit-2": [
            (-60.0, 6.0, 2.0, 1.0, 12.0),     # hw/lw=2.0 límite
            (-90.0, 9.0, 3.0, 1.5, 18.0),
        ],
        # GRUPO C - Wall piers (cargas moderadas)
        "C1-WPColumn": [
            (-80.0, 8.0, 3.0, 2.0, 15.0),     # wall pier columna
            (-120.0, 12.0, 4.0, 3.0, 22.0),
        ],
        "C2-WPWall": [
            (-60.0, 6.0, 2.0, 1.5, 12.0),     # wall pier muro
            (-90.0, 9.0, 3.0, 2.0, 18.0),
        ],
        # GRUPO D - Cargas ligeras (deben pasar OK)
        "D1-LightLoad": [
            (-30.0, 3.0, 1.0, 0.5, 5.0),      # carga muy baja
            (-45.0, 4.0, 1.5, 0.8, 8.0),
        ],
        "D2-SquatOK": [
            (-40.0, 4.0, 1.0, 1.0, 8.0),      # muro achaparrado ligero
            (-60.0, 6.0, 1.5, 1.5, 12.0),
        ],
        # GRUPO E - Casos especiales de carga
        "E1-Tension": [
            (10.0, 5.0, 2.0, 1.0, 8.0),       # TRACCIÓN (P positivo)
            (20.0, 8.0, 3.0, 1.5, 12.0),      # más tracción
        ],
        "E2-HighM": [
            (-20.0, 3.0, 1.0, 0.5, 25.0),     # bajo axial, alto momento
            (-30.0, 4.0, 1.5, 0.8, 40.0),     # aún más momento
        ],
    }

    for label, story, thickness, width, material, height in piers_config:
        forces = forces_config[label]

        for i, (combo_name, step_type) in enumerate(combos):
            P, V2, V3, M2, M3 = forces[i]

            # Top location
            pier_forces_data.append({
                "Story": story,
                "Pier": label,
                "Output Case": combo_name,
                "Case Type": "Combination",
                "Step Type": step_type,
                "Location": "Top",
                "P": P,
                "V2": V2,
                "V3": V3,
                "T": 0.0,
                "M2": M2,
                "M3": M3,
            })

            # Bottom location (momentos ligeramente mayores)
            pier_forces_data.append({
                "Story": story,
                "Pier": label,
                "Output Case": combo_name,
                "Case Type": "Combination",
                "Step Type": step_type,
                "Location": "Bottom",
                "P": P * 1.1,  # Un poco más de carga en la base
                "V2": V2,
                "V3": V3,
                "T": 0.0,
                "M2": M2 * 0.8,
                "M3": M3 * 1.2,  # Momento mayor en la base
            })

    df_pier_forces = pd.DataFrame(pier_forces_data)

    # =========================================================================
    # Tabla 3: Material Properties
    # =========================================================================
    materials_data = [
        {"Material": "H30", "Type": "Concrete", "E": 25000, "fc": 25.0},
    ]
    df_materials = pd.DataFrame(materials_data)

    # =========================================================================
    # Crear Excel con marcadores TABLE:
    # =========================================================================
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja con todas las tablas (formato ETABS)
        workbook = writer.book
        worksheet = workbook.create_sheet("ETABS Data", 0)

        current_row = 1

        # Tabla: Pier Section Properties
        worksheet.cell(row=current_row, column=1, value="TABLE:  Pier Section Properties")
        current_row += 1

        # Headers
        for col, header in enumerate(df_pier_props.columns, 1):
            worksheet.cell(row=current_row, column=col, value=header)
        current_row += 1

        # Data
        for _, row in df_pier_props.iterrows():
            for col, value in enumerate(row, 1):
                worksheet.cell(row=current_row, column=col, value=value)
            current_row += 1

        current_row += 2  # Espacio entre tablas

        # Tabla: Pier Forces
        worksheet.cell(row=current_row, column=1, value="TABLE:  Pier Forces")
        current_row += 1

        # Headers
        for col, header in enumerate(df_pier_forces.columns, 1):
            worksheet.cell(row=current_row, column=col, value=header)
        current_row += 1

        # Data
        for _, row in df_pier_forces.iterrows():
            for col, value in enumerate(row, 1):
                worksheet.cell(row=current_row, column=col, value=value)
            current_row += 1

        current_row += 2

        # Tabla: Material Properties
        worksheet.cell(row=current_row, column=1, value="TABLE:  Material Properties 02 - Basic Mechanical Properties")
        current_row += 1

        for col, header in enumerate(df_materials.columns, 1):
            worksheet.cell(row=current_row, column=col, value=header)
        current_row += 1

        for _, row in df_materials.iterrows():
            for col, value in enumerate(row, 1):
                worksheet.cell(row=current_row, column=col, value=value)
            current_row += 1

    output.seek(0)
    return output.getvalue()


def save_test_excel(output_path: str = None):
    """Guarda el Excel de prueba en disco."""
    if output_path is None:
        # Guardar en la carpeta examples
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, "examples", "test_data_5piers.xlsx")

    excel_bytes = generate_test_excel()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(excel_bytes)

    print(f"Excel de prueba guardado en: {output_path}")
    print("\nPiers generados (11 casos de prueba):")
    print("\nGRUPO A - Sobrecargados (NO OK esperado):")
    print("  - A1-Overload: 20x20 cm columna")
    print("  - A2-Overload: 20x50 cm")
    print("\nGRUPO B - Limites de clasificacion:")
    print("  - B1-Limit-4: 20x80 cm (lw/tw=4.0 limite)")
    print("  - B2-Slender: 20x120 cm (hw/lw=2.5 esbelto)")
    print("  - B3-Limit-2: 25x125 cm (hw/lw=2.0 limite)")
    print("\nGRUPO C - Wall piers (18.10.8):")
    print("  - C1-WPColumn: 30x100 cm (lw/tw=3.3, hw/lw<2)")
    print("  - C2-WPWall: 20x100 cm (lw/tw=5.0, hw/lw<2)")
    print("\nGRUPO D - Cargas ligeras (OK esperado):")
    print("  - D1-LightLoad: 30x150 cm")
    print("  - D2-SquatOK: 25x200 cm (achaparrado)")
    print("\nGRUPO E - Casos especiales:")
    print("  - E1-Tension: 20x100 cm (traccion)")
    print("  - E2-HighM: 20x100 cm (alto momento)")
    print("\nCombinaciones de carga:")
    print("  - 1.4D")
    print("  - 1.2D+1.6L")

    return output_path


if __name__ == "__main__":
    save_test_excel()
