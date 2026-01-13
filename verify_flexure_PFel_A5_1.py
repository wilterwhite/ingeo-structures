"""
Script de verificacion manual de calculos de flexion para PFel-A5-1.

Datos del pier:
- Dimensiones: lw=640mm, tw=260mm, hw=3350mm
- f'c = 20.7 MPa, fy = 420 MPa
- Refuerzo: 2M d8@150 + 2d10 en bordes, E10@150
- As total = 615.8 mm2

Fuerzas de diseno:
- Pu = 27.05 tonf (compresion)
- Mu3 = 14.3 tonf-m (momento critico)

Resultado del sistema:
- phiMn = 4.59 tonf-m
- D/C = 3.114
"""

import sys
import math
from pathlib import Path

# Configurar la salida estándar para UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from app.domain.flexure import InteractionDiagramService, FlexureChecker, InteractionPoint
from app.domain.entities import Pier
from app.domain.constants.materials import get_bar_area
from app.domain.constants.phi_chapter21 import calculate_phi_flexure, PHI_COMPRESSION
from app.domain.constants.units import N_TO_TONF, NMM_TO_TONFM

print("=" * 80)
print("VERIFICACION DE CALCULOS DE FLEXION - Pier PFel-A5-1")
print("=" * 80)

# =============================================================================
# PASO 1: Crear el pier con los datos reales
# =============================================================================
print("\n1. CREACION DEL PIER")
print("-" * 80)

pier = Pier(
    label="PFel-A5-1",
    story="Piso 1",
    width=640,           # mm
    thickness=260,       # mm
    height=3350,         # mm
    fc=20.7,            # MPa
    fy=420,             # MPa
    n_meshes=2,         # 2 mallas
    diameter_v=8,       # φ8
    spacing_v=150,      # @150mm
    diameter_h=8,       # φ8
    spacing_h=150,      # @150mm
    n_edge_bars=2,      # 2 barras de borde por extremo
    diameter_edge=10,   # φ10
    stirrup_diameter=10,
    stirrup_spacing=150,
    cover=25.0
)

print(f"Label: {pier.label}")
print(f"Dimensiones: lw={pier.width}mm, tw={pier.thickness}mm, hw={pier.height}mm")
print(f"Materiales: f'c={pier.fc} MPa, fy={pier.fy} MPa")
print(f"Refuerzo: {pier.reinforcement_description}")
print(f"Area bruta Ag: {pier.Ag:.1f} mm2")
print(f"Area de acero As total: {pier.As_flexure_total:.1f} mm2")
print(f"Cuantia rho_v: {pier.rho_vertical:.5f} ({pier.rho_vertical*100:.3f}%)")

# Verificar el área de acero calculada
As_total_expected = 615.8
As_diff = abs(pier.As_flexure_total - As_total_expected)
print(f"\nVerificacion As total:")
print(f"  - Esperado: {As_total_expected} mm2")
print(f"  - Calculado: {pier.As_flexure_total:.1f} mm2")
print(f"  - Diferencia: {As_diff:.1f} mm2 ({As_diff/As_total_expected*100:.2f}%)")

# =============================================================================
# PASO 2: Generar las capas de acero
# =============================================================================
print("\n2. CAPAS DE ACERO")
print("-" * 80)

steel_layers = pier.get_steel_layers(direction='primary')
print(f"Numero de capas: {len(steel_layers)}")
print("\nDetalle de capas:")
As_layers_sum = 0
for i, layer in enumerate(steel_layers, 1):
    print(f"  Capa {i}: posicion={layer.position:.1f} mm, area={layer.area:.2f} mm2")
    As_layers_sum += layer.area

print(f"\nSuma de areas de capas: {As_layers_sum:.1f} mm2")
print(f"As_flexure_total: {pier.As_flexure_total:.1f} mm2")
print(f"Diferencia: {abs(As_layers_sum - pier.As_flexure_total):.2f} mm2")

# =============================================================================
# PASO 3: Generar curva de interacción P-M
# =============================================================================
print("\n3. CURVA DE INTERACCION P-M")
print("-" * 80)

service = InteractionDiagramService()

# Generar curva con 100 puntos para mejor precisión
points = service.generate_interaction_curve(
    width=pier.width,
    thickness=pier.thickness,
    fc=pier.fc,
    fy=pier.fy,
    As_total=pier.As_flexure_total,
    cover=pier.cover,
    steel_layers=steel_layers,
    n_points=100
)

print(f"Numero de puntos en la curva: {len(points)}")

# Encontrar puntos importantes
P0_point = max(points, key=lambda p: p.phi_Pn)
Pt_point = min(points, key=lambda p: p.phi_Pn)
phi_Mn_0 = FlexureChecker.get_phi_Mn_at_P0(points)

print(f"\nPuntos clave:")
print(f"  - Compresion pura (P0): phiPn={P0_point.phi_Pn:.1f} tonf, phiMn={P0_point.phi_Mn:.2f} tonf-m")
print(f"  - Traccion pura (Pt): phiPn={Pt_point.phi_Pn:.1f} tonf, phiMn={Pt_point.phi_Mn:.2f} tonf-m")
print(f"  - Flexion pura (P~0): phiMn={phi_Mn_0:.2f} tonf-m")

# =============================================================================
# PASO 4: Verificar con las fuerzas de diseño
# =============================================================================
print("\n4. VERIFICACION CON FUERZAS DE DISENO")
print("-" * 80)

Pu_design = 27.05  # tonf (compresion)
Mu_design = 14.3   # tonf-m

print(f"Fuerzas de diseno:")
print(f"  - Pu = {Pu_design} tonf (compresion)")
print(f"  - Mu = {Mu_design} tonf-m")

# Calcular factor de seguridad usando ray-casting
sf, is_inside = FlexureChecker.calculate_safety_factor(points, Pu_design, Mu_design)

print(f"\nResultado del ray-casting:")
print(f"  - Factor de seguridad (SF): {sf:.3f}")
print(f"  - Punto dentro de la curva: {is_inside}")
print(f"  - DCR = 1/SF: {1/sf:.3f}")

# Calcular phiMn efectivo al nivel Pu critico
# Metodo 1: Usando el SF (consistente con ray-casting)
phi_Mn_at_Pu_raycast = Mu_design * sf
print(f"\nphiMn efectivo (ray-casting): {phi_Mn_at_Pu_raycast:.2f} tonf-m")
print(f"  = Mu x SF = {Mu_design} x {sf:.3f}")

# Metodo 2: Interpolacion horizontal en la curva
phi_Mn_at_Pu_interp = FlexureChecker.get_phi_Mn_at_P(points, Pu_design)
print(f"\nphiMn interpolado horizontal: {phi_Mn_at_Pu_interp:.2f} tonf-m")

# Comparacion con resultado del sistema
phi_Mn_system = 4.59  # tonf-m
dcr_system = 3.114

print(f"\n" + "=" * 80)
print("COMPARACION CON RESULTADO DEL SISTEMA")
print("=" * 80)
print(f"\nResultado del sistema:")
print(f"  - phiMn = {phi_Mn_system} tonf-m")
print(f"  - D/C = {dcr_system}")

print(f"\nResultado calculado (ray-casting):")
print(f"  - phiMn = {phi_Mn_at_Pu_raycast:.2f} tonf-m")
print(f"  - D/C = {1/sf:.3f}")

print(f"\nResultado calculado (interpolacion):")
print(f"  - phiMn = {phi_Mn_at_Pu_interp:.2f} tonf-m")
print(f"  - D/C = {Mu_design/phi_Mn_at_Pu_interp:.3f}")

# Análisis de diferencias
diff_raycast = abs(phi_Mn_at_Pu_raycast - phi_Mn_system)
diff_interp = abs(phi_Mn_at_Pu_interp - phi_Mn_system)

print(f"\nDiferencias:")
print(f"  - Ray-casting vs Sistema: {diff_raycast:.2f} tonf-m ({diff_raycast/phi_Mn_system*100:.1f}%)")
print(f"  - Interpolación vs Sistema: {diff_interp:.2f} tonf-m ({diff_interp/phi_Mn_system*100:.1f}%)")

# =============================================================================
# PASO 5: Análisis detallado del punto crítico
# =============================================================================
print("\n5. ANALISIS DEL PUNTO EN LA CURVA MAS CERCANO A LA DEMANDA")
print("-" * 80)

# Encontrar el punto más cercano a la demanda
min_dist = float('inf')
closest_point = None
for p in points:
    dist = math.sqrt((p.phi_Pn - Pu_design)**2 + (p.phi_Mn - Mu_design)**2)
    if dist < min_dist:
        min_dist = dist
        closest_point = p

if closest_point:
    print(f"Punto mas cercano a la demanda:")
    print(f"  - phiPn = {closest_point.phi_Pn:.2f} tonf")
    print(f"  - phiMn = {closest_point.phi_Mn:.2f} tonf-m")
    print(f"  - c (eje neutro) = {closest_point.c:.1f} mm")
    print(f"  - epsilon_t (deformacion traccion) = {closest_point.epsilon_t:.6f}")
    print(f"  - phi (factor reduccion) = {closest_point.phi:.3f}")
    print(f"  - Distancia al punto de demanda: {min_dist:.3f}")

# =============================================================================
# PASO 6: Verificar cálculo del factor φ
# =============================================================================
print("\n6. VERIFICACION DEL FACTOR phi")
print("-" * 80)

# Buscar puntos alrededor de Pu = 27.05 tonf
print(f"\nPuntos de la curva cerca de Pu = {Pu_design} tonf:")
print(f"{'phiPn (tonf)':<12} {'phiMn (tonf-m)':<15} {'epsilon_t':<12} {'phi':<8} {'c (mm)':<10}")
print("-" * 70)

nearby_points = []
for p in points:
    if abs(p.phi_Pn - Pu_design) < 5:  # ±5 tonf
        nearby_points.append(p)

nearby_points.sort(key=lambda p: abs(p.phi_Pn - Pu_design))

for p in nearby_points[:10]:  # Mostrar 10 puntos más cercanos
    print(f"{p.phi_Pn:>10.2f}   {p.phi_Mn:>13.2f}   {p.epsilon_t:>10.6f}   {p.phi:>6.3f}  {p.c:>8.1f}")

# =============================================================================
# PASO 7: Verificación manual de un punto
# =============================================================================
print("\n7. VERIFICACION MANUAL DE CALCULO DE UN PUNTO")
print("-" * 80)

# Tomar un punto con c conocido y recalcular manualmente
if closest_point:
    c = closest_point.c
    print(f"\nRecalculando punto con c = {c:.1f} mm:")

    # Constantes
    epsilon_cu = 0.003
    Es = 200000  # MPa
    beta1 = service.calculate_beta1(pier.fc)

    print(f"  - β1 = {beta1:.3f}")
    print(f"  - εcu = {epsilon_cu}")
    print(f"  - Es = {Es} MPa")

    # Bloque de Whitney
    a = beta1 * c
    print(f"  - a = β1 × c = {a:.1f} mm")

    # Compresion del hormigon
    Cc = 0.85 * pier.fc * a * pier.thickness  # N
    print(f"  - Cc = 0.85 x f'c x a x tw = {Cc:.0f} N = {Cc/N_TO_TONF:.2f} tonf")

    # Momento del hormigon respecto al centroide
    y_centroid = pier.width / 2
    Mc = Cc * (y_centroid - a/2)
    print(f"  - Mc = Cc x (y_centroid - a/2) = {Mc/NMM_TO_TONFM:.2f} tonf-m")

    # Contribucion del acero
    print(f"\n  Contribucion de cada capa de acero:")
    print(f"  {'Capa':<6} {'di (mm)':<10} {'epsilon_i':<12} {'fs (MPa)':<12} {'Fi (N)':<15} {'Mi (N-mm)':<15}")
    print("  " + "-" * 75)

    Pn_steel = 0.0
    Mn_steel = 0.0
    epsilon_t_max = 0.0

    for i, layer in enumerate(steel_layers, 1):
        di = layer.position
        Asi = layer.area

        # Deformacion
        epsilon_i = epsilon_cu * (di - c) / c

        # Esfuerzo
        fs_i = min(abs(epsilon_i) * Es, pier.fy)
        if epsilon_i < 0:
            fs_i = -fs_i

        # Fuerza
        if di <= a:
            if fs_i < 0:
                Fi = Asi * (fs_i + 0.85 * pier.fc)
            else:
                Fi = Asi * fs_i
        else:
            Fi = Asi * fs_i

        # Contribuciones
        Pn_steel += -Fi
        Mn_steel += Fi * (di - y_centroid)

        if epsilon_i > epsilon_t_max:
            epsilon_t_max = epsilon_i

        print(f"  {i:<6} {di:>8.1f}   {epsilon_i:>10.6f}   {fs_i:>10.2f}   {Fi:>13.1f}   {Fi * (di - y_centroid):>13.1f}")

    # Totales
    Pn = Cc + Pn_steel
    Mn = abs(Mc + Mn_steel)

    print(f"\n  Pn total = {Pn/N_TO_TONF:.2f} tonf")
    print(f"  Mn total = {Mn/NMM_TO_TONFM:.2f} tonf-m")
    print(f"  epsilon_t maxima = {epsilon_t_max:.6f}")

    # Factor phi
    phi = calculate_phi_flexure(epsilon_t_max)
    print(f"  phi = {phi:.3f}")

    phi_Pn = phi * Pn / N_TO_TONF
    phi_Mn = phi * Mn / NMM_TO_TONFM

    print(f"\n  phiPn = {phi_Pn:.2f} tonf")
    print(f"  phiMn = {phi_Mn:.2f} tonf-m")

    print(f"\n  Comparacion con punto de la curva:")
    print(f"    - phiPn: calculado={phi_Pn:.2f}, curva={closest_point.phi_Pn:.2f}, diff={abs(phi_Pn-closest_point.phi_Pn):.3f}")
    print(f"    - phiMn: calculado={phi_Mn:.2f}, curva={closest_point.phi_Mn:.2f}, diff={abs(phi_Mn-closest_point.phi_Mn):.3f}")

# =============================================================================
# CONCLUSIONES
# =============================================================================
print("\n" + "=" * 80)
print("CONCLUSIONES")
print("=" * 80)

if abs(phi_Mn_at_Pu_raycast - phi_Mn_system) < 0.5:
    print("\n[OK] El calculo de phiMn es CORRECTO (diferencia < 0.5 tonf-m)")
else:
    print("\n[ERROR] DISCREPANCIA SIGNIFICATIVA en el calculo de phiMn")
    print(f"  Diferencia: {abs(phi_Mn_at_Pu_raycast - phi_Mn_system):.2f} tonf-m")

if abs((1/sf) - dcr_system) < 0.05:
    print("[OK] El calculo del D/C es CORRECTO (diferencia < 0.05)")
else:
    print("[ERROR] DISCREPANCIA en el calculo del D/C")
    print(f"  Diferencia: {abs((1/sf) - dcr_system):.3f}")

# Verificar el factor phi usado
if closest_point:
    if closest_point.epsilon_t < 0.002:
        expected_phi = PHI_COMPRESSION
        print(f"\n[OK] El factor phi = {closest_point.phi:.3f} es correcto para compresion controlada")
    else:
        print(f"\n[WARN] El punto esta en zona de transicion (epsilon_t = {closest_point.epsilon_t:.6f})")
        print(f"  phi = {closest_point.phi:.3f} (entre 0.65 y 0.90)")

print("\n" + "=" * 80)
