"""
Script para crear archivo edge_cases_complete.xlsx con todos los tipos de elementos.
"""
import openpyxl
from openpyxl import Workbook

wb = Workbook()

# ============================================================================
# Sheet 1: Pier Section Properties
# ============================================================================
ws1 = wb.active
ws1.title = 'Pier Section Properties'

# Header row (TABLE name merged across columns)
ws1['A1'] = 'TABLE:  Pier Section Properties'

# Column headers
headers1 = ['Story', 'Pier', 'AxisAngle', '# Area Objects', '# Line Objects',
            'Width Bottom', 'Thickness Bottom', 'Width Top', 'Thickness Top', 'Material']
for col, h in enumerate(headers1, 1):
    ws1.cell(row=2, column=col, value=h)

# Units row
units1 = ['', '', 'deg', '', '', 'm', 'm', 'm', 'm', '']
for col, u in enumerate(units1, 1):
    ws1.cell(row=3, column=col, value=u)

# Data rows - 4 piers
piers = [
    # Story, Pier, Angle, AreaObj, LineObj, WBottom, TBottom, WTop, TTop, Material
    ('Piso1', 'P1', 90, 3, 0, 0.6, 0.26, 0.6, 0.26, '3000Psi'),    # Wall pier lw/tw < 6
    ('Piso1', 'P2', 0, 6, 0, 1.5, 0.21, 1.5, 0.21, '3000Psi'),     # Wall slender
    ('Piso1', 'P3', 0, 12, 0, 3.0, 0.20, 3.0, 0.20, '3000Psi'),    # Wall muy slender
    ('Piso1', 'P4', 90, 1, 0, 0.15, 0.15, 0.15, 0.15, '3000Psi'),  # Pier-column
]
for row_idx, pier in enumerate(piers, 4):
    for col, val in enumerate(pier, 1):
        ws1.cell(row=row_idx, column=col, value=val)

# ============================================================================
# Sheet 2: Pier Forces
# ============================================================================
ws2 = wb.create_sheet('Pier Forces')
ws2['A1'] = 'TABLE:  Pier Forces'

headers2 = ['Story', 'Pier', 'Output Case', 'Case Type', 'Step Type', 'Location',
            'P', 'V2', 'V3', 'T', 'M2', 'M3']
for col, h in enumerate(headers2, 1):
    ws2.cell(row=2, column=col, value=h)

units2 = ['', '', '', '', '', '', 'tonf', 'tonf', 'tonf', 'tonf-m', 'tonf-m', 'tonf-m']
for col, u in enumerate(units2, 1):
    ws2.cell(row=3, column=col, value=u)

# Fuerzas por pier (3 combos x 2 locations x 4 piers)
pier_forces = []
combos = [('1.2D+1.6L', 'Combination', ''), ('1.4X+1.2D+1.0L', 'Combination', 'Max'), ('1.4Y+1.2D+1.0L', 'Combination', 'Max')]

# P1 (wall pier): P=-30, V2=8, V3=1, M2=2, M3=10
for combo, ctype, step in combos:
    pier_forces.append(('Piso1', 'P1', combo, ctype, step, 'Top', -30, 8, 1, 0.5, 2, 10))
    pier_forces.append(('Piso1', 'P1', combo, ctype, step, 'Bottom', -25, 6, 0.8, 0.3, 1.5, 8))
# P2 (wall slender): P=-40, V2=12, V3=1.5, M2=3, M3=15
for combo, ctype, step in combos:
    pier_forces.append(('Piso1', 'P2', combo, ctype, step, 'Top', -40, 12, 1.5, 0.8, 3, 15))
    pier_forces.append(('Piso1', 'P2', combo, ctype, step, 'Bottom', -35, 10, 1.2, 0.5, 2.5, 12))
# P3 (muy slender): P=-50, V2=15, V3=2, M2=4, M3=20
for combo, ctype, step in combos:
    pier_forces.append(('Piso1', 'P3', combo, ctype, step, 'Top', -50, 15, 2, 1.0, 4, 20))
    pier_forces.append(('Piso1', 'P3', combo, ctype, step, 'Bottom', -45, 12, 1.5, 0.7, 3, 16))
# P4 (pier-column small): P=-15, V2=3, V3=2, M2=1, M3=3
for combo, ctype, step in combos:
    pier_forces.append(('Piso1', 'P4', combo, ctype, step, 'Top', -15, 3, 2, 0.2, 1, 3))
    pier_forces.append(('Piso1', 'P4', combo, ctype, step, 'Bottom', -12, 2.5, 1.5, 0.15, 0.8, 2.5))

for row_idx, force in enumerate(pier_forces, 4):
    for col, val in enumerate(force, 1):
        ws2.cell(row=row_idx, column=col, value=val)

print(f'Pier Forces: {len(pier_forces)} filas')

# ============================================================================
# Sheet 3: Spandrel Section Properties (Drop Beams)
# ============================================================================
ws3 = wb.create_sheet('Spandrel Section Properties')
ws3['A1'] = 'TABLE:  Spandrel Section Properties'

headers3 = ['Story', 'Spandrel', '# Area Objects', '# Line Objects', 'Length',
            'Depth Left', 'Thickness Left', 'Depth Right', 'Thickness Right', 'Material']
for col, h in enumerate(headers3, 1):
    ws3.cell(row=2, column=col, value=h)

units3 = ['', '', '', '', 'm', 'm', 'm', 'm', 'm', '']
for col, u in enumerate(units3, 1):
    ws3.cell(row=3, column=col, value=u)

spandrels = [
    ('Piso1', 'S1', 2, 0, 0.45, 0.66, 0.26, 0.66, 0.26, '3000Psi'),  # Drop beam corta
    ('Piso1', 'S2', 4, 0, 0.90, 0.66, 0.21, 0.66, 0.21, '3000Psi'),  # Drop beam tipica
    ('Piso1', 'S3', 3, 0, 1.20, 0.40, 0.20, 0.40, 0.20, '3000Psi'),  # Drop beam esbelta
]
for row_idx, span in enumerate(spandrels, 4):
    for col, val in enumerate(span, 1):
        ws3.cell(row=row_idx, column=col, value=val)

# ============================================================================
# Sheet 4: Spandrel Forces
# ============================================================================
ws4 = wb.create_sheet('Spandrel Forces')
ws4['A1'] = 'TABLE:  Spandrel Forces'

headers4 = ['Story', 'Spandrel', 'Output Case', 'Case Type', 'Step Type', 'Location',
            'P', 'V2', 'V3', 'T', 'M2', 'M3']
for col, h in enumerate(headers4, 1):
    ws4.cell(row=2, column=col, value=h)

units4 = ['', '', '', '', '', '', 'tonf', 'tonf', 'tonf', 'tonf-m', 'tonf-m', 'tonf-m']
for col, u in enumerate(units4, 1):
    ws4.cell(row=3, column=col, value=u)

spandrel_forces = []
# S1: P=-6, V2=8, M3=3
for combo, ctype, step in combos:
    spandrel_forces.append(('Piso1', 'S1', combo, ctype, step, 'Left', -6, 8, 0.2, 0.1, 0.1, 2))
    spandrel_forces.append(('Piso1', 'S1', combo, ctype, step, 'Right', -6, 8, 0.2, 0.1, 0.1, 3))
# S2: P=-8, V2=10, M3=4
for combo, ctype, step in combos:
    spandrel_forces.append(('Piso1', 'S2', combo, ctype, step, 'Left', -8, 10, 0.3, 0.15, 0.15, 3))
    spandrel_forces.append(('Piso1', 'S2', combo, ctype, step, 'Right', -8, 10, 0.3, 0.15, 0.15, 4))
# S3: P=-5, V2=6, M3=2.5
for combo, ctype, step in combos:
    spandrel_forces.append(('Piso1', 'S3', combo, ctype, step, 'Left', -5, 6, 0.15, 0.1, 0.1, 2))
    spandrel_forces.append(('Piso1', 'S3', combo, ctype, step, 'Right', -5, 6, 0.15, 0.1, 0.1, 2.5))

for row_idx, force in enumerate(spandrel_forces, 4):
    for col, val in enumerate(force, 1):
        ws4.cell(row=row_idx, column=col, value=val)

print(f'Spandrel Forces: {len(spandrel_forces)} filas')

# ============================================================================
# Sheet 5: Frame Sec Def - Conc Rect (Columns + Beams)
# ============================================================================
ws5 = wb.create_sheet('Frame Sec Def - Conc Rect')
ws5['A1'] = 'TABLE:  Frame Section Property Definitions - Concrete Rectangular'

headers5 = ['Name', 'Material', 'From File?', 'Depth', 'Width', 'Design Type']
for col, h in enumerate(headers5, 1):
    ws5.cell(row=2, column=col, value=h)

units5 = ['', '', '', 'm', 'm', '']
for col, u in enumerate(units5, 1):
    ws5.cell(row=3, column=col, value=u)

frame_sections = [
    # Columnas
    ('COL_12x12', 'Concreto28', 'No', 0.12, 0.12, 'Column'),  # Strut
    ('COL_14x14', 'Concreto28', 'No', 0.14, 0.14, 'Column'),  # Strut
    ('COL_15x12', 'Concreto28', 'No', 0.15, 0.12, 'Column'),  # Crossties
    ('COL_15x15', 'Concreto28', 'No', 0.15, 0.15, 'Column'),  # Normal
    ('COL_20x20', 'Concreto28', 'No', 0.20, 0.20, 'Column'),  # Normal
    ('COL_40x20', 'Concreto28', 'No', 0.40, 0.20, 'Column'),  # Normal
    # Vigas
    ('V12x29', 'Concreto28', 'No', 0.29, 0.12, 'Beam'),
    ('V20x35', 'Concreto28', 'No', 0.35, 0.20, 'Beam'),
    ('V20x70', 'Concreto28', 'No', 0.70, 0.20, 'Beam'),
]
for row_idx, sec in enumerate(frame_sections, 4):
    for col, val in enumerate(sec, 1):
        ws5.cell(row=row_idx, column=col, value=val)

# ============================================================================
# Sheet 6: Frame Assigns - Sect Prop
# ============================================================================
ws6 = wb.create_sheet('Frame Assigns - Sect Prop')
ws6['A1'] = 'TABLE:  Frame Assignments - Section Properties'

headers6 = ['Story', 'Label', 'Section Property']
for col, h in enumerate(headers6, 1):
    ws6.cell(row=2, column=col, value=h)

assigns = [
    ('Piso1', 'C1', 'COL_12x12'),
    ('Piso1', 'C2', 'COL_14x14'),
    ('Piso1', 'C3', 'COL_15x12'),
    ('Piso1', 'C4', 'COL_15x15'),
    ('Piso1', 'C5', 'COL_20x20'),
    ('Piso1', 'C6', 'COL_40x20'),
    ('Piso1', 'B1', 'V12x29'),
    ('Piso1', 'B2', 'V20x35'),
    ('Piso1', 'B3', 'V20x70'),
]
for row_idx, assign in enumerate(assigns, 3):
    for col, val in enumerate(assign, 1):
        ws6.cell(row=row_idx, column=col, value=val)

# ============================================================================
# Sheet 7: Element Forces - Columns
# ============================================================================
ws7 = wb.create_sheet('Element Forces - Columns')
ws7['A1'] = 'TABLE:  Element Forces - Columns'

headers7 = ['Story', 'Column', 'Unique Name', 'Output Case', 'Case Type', 'Step Type',
            'Station', 'P', 'V2', 'V3', 'T', 'M2', 'M3']
for col, h in enumerate(headers7, 1):
    ws7.cell(row=2, column=col, value=h)

units7 = ['', '', '', '', '', '', 'm', 'tonf', 'tonf', 'tonf', 'tonf-m', 'tonf-m', 'tonf-m']
for col, u in enumerate(units7, 1):
    ws7.cell(row=3, column=col, value=u)

col_forces = []
height = 2.8  # metros

# Fuerzas por columna (P, V2, V3, M2, M3) y variaciones por combo
col_loads = {
    'C1': [(-5, 0.5, 0.3, 0.5, 0.8), (-3, 0.8, 0.5, 0.6, 1.0), (-4, 0.6, 0.4, 0.55, 0.9)],
    'C2': [(-8, 0.6, 0.4, 0.6, 1.0), (-6, 1.0, 0.6, 0.8, 1.2), (-7, 0.8, 0.5, 0.7, 1.1)],
    'C3': [(-20, 2.0, 1.0, 1.2, 2.0), (-15, 3.0, 1.5, 1.5, 2.5), (-18, 2.5, 1.2, 1.3, 2.2)],
    'C4': [(-30, 2.5, 1.5, 1.5, 2.5), (-25, 4.0, 2.0, 2.0, 3.5), (-28, 3.0, 1.8, 1.8, 3.0)],
    'C5': [(-50, 3.0, 2.0, 2.0, 3.5), (-40, 5.0, 3.0, 2.5, 5.0), (-45, 4.0, 2.5, 2.2, 4.2)],
    'C6': [(-100, 5.0, 3.0, 3.0, 6.0), (-80, 8.0, 5.0, 4.0, 8.0), (-90, 6.5, 4.0, 3.5, 7.0)],
}

unique_id = 1000
for col_name, loads in col_loads.items():
    for i, (combo, ctype, step) in enumerate(combos):
        P, V2, V3, M2, M3 = loads[i]
        # Station 0 (bottom)
        col_forces.append(('Piso1', col_name, str(unique_id), combo, ctype, step, 0, P, V2, V3, 0.1, M2, M3))
        # Station height (top)
        col_forces.append(('Piso1', col_name, str(unique_id), combo, ctype, step, height, P*0.9, V2*0.9, V3*0.9, 0.08, M2*0.8, M3*0.8))
    unique_id += 1

for row_idx, force in enumerate(col_forces, 4):
    for col, val in enumerate(force, 1):
        ws7.cell(row=row_idx, column=col, value=val)

print(f'Column Forces: {len(col_forces)} filas')

# ============================================================================
# Sheet 8: Element Forces - Beams
# ============================================================================
ws8 = wb.create_sheet('Element Forces - Beams')
ws8['A1'] = 'TABLE:  Element Forces - Beams'

headers8 = ['Story', 'Beam', 'Unique Name', 'Output Case', 'Case Type', 'Step Type',
            'Station', 'P', 'V2', 'V3', 'T', 'M2', 'M3']
for col, h in enumerate(headers8, 1):
    ws8.cell(row=2, column=col, value=h)

units8 = ['', '', '', '', '', '', 'm', 'tonf', 'tonf', 'tonf', 'tonf-m', 'tonf-m', 'tonf-m']
for col, u in enumerate(units8, 1):
    ws8.cell(row=3, column=col, value=u)

beam_forces = []
beam_loads = {
    'B1': [(0, 3.5, 4.0), (0, 4.0, 5.0), (0, 3.8, 4.5)],  # (P, V2, M3)
    'B2': [(0, 5.0, 6.0), (0, 6.0, 8.0), (0, 5.5, 7.0)],
    'B3': [(0, 8.0, 10.0), (0, 10.0, 12.0), (0, 9.0, 11.0)],
}
beam_lengths = {'B1': 3.0, 'B2': 4.0, 'B3': 6.0}

unique_id = 2000
for beam_name, loads in beam_loads.items():
    length = beam_lengths[beam_name]
    for i, (combo, ctype, step) in enumerate(combos):
        P, V2, M3 = loads[i]
        # 3 stations: 0, mid, end
        beam_forces.append(('Piso1', beam_name, str(unique_id), combo, ctype, step, 0, P, V2, 0, 0, 0, M3))
        beam_forces.append(('Piso1', beam_name, str(unique_id), combo, ctype, step, length/2, P, 0, 0, 0, 0, M3*1.3))
        beam_forces.append(('Piso1', beam_name, str(unique_id), combo, ctype, step, length, P, -V2, 0, 0, 0, M3))
    unique_id += 1

for row_idx, force in enumerate(beam_forces, 4):
    for col, val in enumerate(force, 1):
        ws8.cell(row=row_idx, column=col, value=val)

print(f'Beam Forces: {len(beam_forces)} filas')

# ============================================================================
# Sheet 9: Section Cut Forces - Analysis (Drop Beams / Vigas Capitel)
# ============================================================================
ws9 = wb.create_sheet('Section Cut Forces - Analysis')
ws9['A1'] = 'TABLE:  Section Cut Forces - Analysis'

headers9 = ['SectionCut', 'Output Case', 'Case Type', 'Step Type',
            'F1', 'F2', 'F3', 'M1', 'M2', 'M3', 'X', 'Y', 'Z']
for col, h in enumerate(headers9, 1):
    ws9.cell(row=2, column=col, value=h)

units9 = ['', '', '', '', 'tonf', 'tonf', 'tonf', 'tonf-m', 'tonf-m', 'tonf-m', 'm', 'm', 'm']
for col, u in enumerate(units9, 1):
    ws9.cell(row=3, column=col, value=u)

# Drop beams: nombre formato "SCut-Losa S01-{espesor}x{ancho} {descripcion}"
# donde espesor y ancho están en cm
drop_beams_data = [
    # Nombre del corte (incluye dimensiones en cm), coords X, Y, Z
    ('SCut-Losa S01-26x66 eje A - C1', 5.0, 7.0, 3.0),    # 260mm x 660mm
    ('SCut-Losa S01-21x66 eje B - C2', 10.0, 7.0, 3.0),   # 210mm x 660mm
    ('SCut-Losa S01-20x40 eje C - C3', 15.0, 7.0, 3.0),   # 200mm x 400mm
]

section_cut_forces = []
for cut_name, x, y, z in drop_beams_data:
    for combo, ctype, step in combos:
        # F1=axial, F2=cortante, F3=cortante secundario
        # M1=torsion, M2=momento secundario, M3=momento principal
        section_cut_forces.append((
            cut_name, combo, ctype, step,
            -5.0,   # F1 (axial, compresión)
            8.0,    # F2 (cortante principal)
            0.5,    # F3 (cortante secundario)
            0.2,    # M1 (torsión)
            0.5,    # M2 (momento secundario)
            5.0,    # M3 (momento principal)
            x, y, z
        ))

for row_idx, force in enumerate(section_cut_forces, 4):
    for col, val in enumerate(force, 1):
        ws9.cell(row=row_idx, column=col, value=val)

print(f'Section Cut Forces (Drop Beams): {len(section_cut_forces)} filas')

# Guardar
wb.save('examples/edge_cases_complete.xlsx')
print('\nArchivo guardado: examples/edge_cases_complete.xlsx')
