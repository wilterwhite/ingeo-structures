# scripts/create_test_data.py
"""
Genera archivo de prueba comprehensivo para INGEO Structures.
"""
from openpyxl import Workbook

output_path = 'C:/Users/willi/Github/ingeo-structures/examples/test_data_comprehensive.xlsx'

# ============================================================================
# PIER SECTION PROPERTIES
# ============================================================================
pier_data = [
    ['Story', 'Pier', 'Width Bottom', 'Thickness Bottom', 'Width Top', 'Thickness Top',
     'Material', 'CG Bottom X', 'CG Bottom Y', 'CG Bottom Z', 'CG Top X', 'CG Top Y', 'CG Top Z'],

    # === GRUPO M: Muros CONTINUOS (mismo label, varios pisos) ===
    ['Piso 1', 'M1-Cont', 2.0, 0.25, 2.0, 0.25, 'H30', 0, 0, 0, 0, 0, 3],
    ['Piso 2', 'M1-Cont', 2.0, 0.25, 2.0, 0.25, 'H30', 0, 0, 3, 0, 0, 6],
    ['Piso 3', 'M1-Cont', 2.0, 0.25, 2.0, 0.25, 'H30', 0, 0, 6, 0, 0, 9],

    ['Piso 1', 'M2-Cont', 1.5, 0.20, 1.5, 0.20, 'H30', 5, 0, 0, 5, 0, 3],
    ['Piso 2', 'M2-Cont', 1.5, 0.20, 1.5, 0.20, 'H30', 5, 0, 3, 5, 0, 6],

    # === GRUPO W: Clasificación WALL vs COLUMN ===
    ['Piso 1', 'W1-Column', 0.6, 0.20, 0.6, 0.20, 'H30', 10, 0, 0, 10, 0, 3],  # lw/tw=3
    ['Piso 1', 'W2-Wall', 1.2, 0.20, 1.2, 0.20, 'H30', 15, 0, 0, 15, 0, 3],    # lw/tw=6

    # === GRUPO P: Wall PIERS (hw/lw < 2) ===
    ['Piso 1', 'P1-WPCol', 0.5, 0.25, 0.5, 0.25, 'H30', 20, 0, 0, 20, 0, 0.8],   # lw/tw=2
    ['Piso 1', 'P2-WPAlt', 1.0, 0.25, 1.0, 0.25, 'H30', 25, 0, 0, 25, 0, 1.5],   # lw/tw=4
    ['Piso 1', 'P3-WPWall', 1.5, 0.20, 1.5, 0.20, 'H30', 30, 0, 0, 30, 0, 2.5],  # lw/tw=7.5

    # === GRUPO S: ESBELTEZ ===
    ['Piso 1', 'S1-Short', 1.0, 0.30, 1.0, 0.30, 'H30', 35, 0, 0, 35, 0, 2.5],
    ['Piso 1', 'S2-Slender', 1.0, 0.15, 1.0, 0.15, 'H30', 40, 0, 0, 40, 0, 4.0],

    # === GRUPO H: hw/lw (Squat vs Slender walls) ===
    ['Piso 1', 'H1-Squat', 3.0, 0.25, 3.0, 0.25, 'H30', 45, 0, 0, 45, 0, 3.0],   # hw/lw=1.0
    ['Piso 1', 'H2-Trans', 1.8, 0.25, 1.8, 0.25, 'H30', 50, 0, 0, 50, 0, 3.0],   # hw/lw=1.67
    ['Piso 1', 'H3-Tall', 1.2, 0.25, 1.2, 0.25, 'H30', 55, 0, 0, 55, 0, 3.0],    # hw/lw=2.5

    # === GRUPO F: CASOS DE FALLA ===
    ['Piso 1', 'F1-FlexFail', 0.8, 0.20, 0.8, 0.20, 'H25', 60, 0, 0, 60, 0, 3],
    ['Piso 1', 'F2-ShearFail', 1.0, 0.15, 1.0, 0.15, 'H25', 65, 0, 0, 65, 0, 3],

    # === GRUPO C: Diferentes CONCRETOS ===
    ['Piso 1', 'C1-H25', 1.5, 0.25, 1.5, 0.25, 'H25', 70, 0, 0, 70, 0, 3],
    ['Piso 1', 'C2-H40', 1.5, 0.25, 1.5, 0.25, 'H40', 75, 0, 0, 75, 0, 3],

    # === GRUPO T: TRACCIÓN ===
    ['Piso 1', 'T1-Tension', 1.0, 0.20, 1.0, 0.20, 'H30', 80, 0, 0, 80, 0, 3],
]

# ============================================================================
# PIER FORCES
# ============================================================================
def generate_forces(story, pier, P_base, V2_base, V3_base, M2_base, M3_base, has_seismic=True):
    """Genera fuerzas para un pier con múltiples combinaciones."""
    rows = []
    combos = [
        ('1.4D', 1.4, 0),
        ('1.2D+1.6L', 1.5, 0),
    ]
    if has_seismic:
        combos.extend([
            ('1.2D+1.0E', 1.2, 1.0),
            ('0.9D+1.0E', 0.9, 1.0),
        ])

    for combo, dead_factor, seis_factor in combos:
        P = round(P_base * dead_factor, 1)
        V2 = round(V2_base * dead_factor + V2_base * 0.5 * seis_factor, 1)
        V3 = round(V3_base * dead_factor + V3_base * 0.3 * seis_factor, 1)
        M2 = round(M2_base * dead_factor + M2_base * 0.3 * seis_factor, 1)
        M3 = round(M3_base * dead_factor + M3_base * 0.5 * seis_factor, 1)

        rows.append([story, pier, combo, 'Combination', 'Max', 'Top', P, V2, V3, 0, M2, M3])
        rows.append([story, pier, combo, 'Combination', 'Max', 'Bottom',
                    round(P * 1.1, 1), V2, V3, 0, round(M2 * 0.8, 1), round(M3 * 1.2, 1)])

    return rows

forces_data = [
    ['Story', 'Pier', 'Output Case', 'Case Type', 'Step Type', 'Location', 'P', 'V2', 'V3', 'T', 'M2', 'M3'],
]

# Muros continuos
for i, story in enumerate(['Piso 1', 'Piso 2', 'Piso 3']):
    forces_data.extend(generate_forces(story, 'M1-Cont', -80 + i*10, 8, 3, 2, 15))

for story in ['Piso 1', 'Piso 2']:
    forces_data.extend(generate_forces(story, 'M2-Cont', -60, 6, 2, 1.5, 12))

# Wall vs Column
forces_data.extend(generate_forces('Piso 1', 'W1-Column', -100, 10, 4, 3, 20))
forces_data.extend(generate_forces('Piso 1', 'W2-Wall', -80, 8, 3, 2, 15))

# Wall piers
forces_data.extend(generate_forces('Piso 1', 'P1-WPCol', -120, 15, 5, 4, 25))
forces_data.extend(generate_forces('Piso 1', 'P2-WPAlt', -100, 12, 4, 3, 20))
forces_data.extend(generate_forces('Piso 1', 'P3-WPWall', -80, 10, 3, 2, 18))

# Esbeltez
forces_data.extend(generate_forces('Piso 1', 'S1-Short', -60, 6, 2, 1, 10))
forces_data.extend(generate_forces('Piso 1', 'S2-Slender', -40, 5, 2, 1.5, 12))

# hw/lw
forces_data.extend(generate_forces('Piso 1', 'H1-Squat', -100, 20, 5, 2, 30))
forces_data.extend(generate_forces('Piso 1', 'H2-Trans', -80, 12, 4, 2, 20))
forces_data.extend(generate_forces('Piso 1', 'H3-Tall', -60, 8, 3, 2, 15))

# Casos de falla
forces_data.extend(generate_forces('Piso 1', 'F1-FlexFail', -30, 5, 2, 1, 80))
forces_data.extend(generate_forces('Piso 1', 'F2-ShearFail', -50, 60, 25, 2, 15))

# Diferentes concretos
forces_data.extend(generate_forces('Piso 1', 'C1-H25', -70, 7, 3, 2, 14))
forces_data.extend(generate_forces('Piso 1', 'C2-H40', -90, 9, 4, 2.5, 18))

# Tracción
forces_data.extend(generate_forces('Piso 1', 'T1-Tension', 30, 8, 3, 2, 15))

# ============================================================================
# MATERIAL PROPERTIES
# ============================================================================
material_data = [
    ['Material', 'Type', 'E', 'fc'],
    ['H25', 'Concrete', 23500, 25],
    ['H30', 'Concrete', 25000, 30],
    ['H40', 'Concrete', 28000, 40],
]

# ============================================================================
# CREAR EXCEL
# ============================================================================
wb = Workbook()
ws = wb.active
ws.title = 'ETABS Data'

ws.append(['TABLE:  Pier Section Properties'])
for row in pier_data:
    ws.append(row)

ws.append([])

ws.append(['TABLE:  Pier Forces'])
for row in forces_data:
    ws.append(row)

ws.append([])

ws.append(['TABLE:  Material Properties 02 - Basic Mechanical Properties'])
for row in material_data:
    ws.append(row)

wb.save(output_path)

print(f'Archivo guardado: {output_path}')
print(f'\nResumen:')
print(f'- Piers: {len(pier_data) - 1} (incluyendo continuos en múltiples pisos)')
print(f'- Pisos: Piso 1, Piso 2, Piso 3')
print(f'- Materiales: H25 (25MPa), H30 (30MPa), H40 (40MPa)')
print(f'- Combinaciones: 1.4D, 1.2D+1.6L, 1.2D+1.0E, 0.9D+1.0E')
print(f'\nCasos de prueba:')
print('  M1-Cont, M2-Cont     : Muros continuos (3 y 2 pisos) - hwcs')
print('  W1-Column, W2-Wall   : Clasificación wall vs column (lw/tw)')
print('  P1-WPCol, P2-WPAlt, P3-WPWall : Wall piers (hw/lw < 2)')
print('  S1-Short, S2-Slender : Esbeltez (lambda)')
print('  H1-Squat, H2-Trans, H3-Tall : Relación hw/lw (alpha_c)')
print('  F1-FlexFail, F2-ShearFail   : Casos que deben fallar')
print('  C1-H25, C2-H40       : Diferentes f\'c')
print('  T1-Tension           : Muro en tracción')
