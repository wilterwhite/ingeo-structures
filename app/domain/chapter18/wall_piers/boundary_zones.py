# app/domain/chapter18/wall_piers/boundary_zones.py
"""
Verificacion de zonas de extremo segun ACI 318-25 §18.10.2.4.

Para muros/pilares con hw/lw >= 2.0 y seccion critica unica:
- (a) rho >= 6*sqrt(f'c)/fy en extremos (0.15*lw x bw)
- (b) Extension vertical >= max(lw, Mu/3Vu)
- (c) No mas del 50% termina en una seccion

Referencias:
- §18.10.2.4(a): Cuantia minima en zonas de extremo
- §18.10.2.4(b): Extension vertical del refuerzo concentrado
- §18.10.2.4(c): Terminacion escalonada del refuerzo
"""
import math
from typing import List
from ..results import BoundaryZoneCheck


# Constantes de conversion
MPA_TO_PSI = 145.04


def check_boundary_zone_reinforcement(
    hw: float,
    lw: float,
    bw: float,
    fc: float,
    fy: float,
    As_left: float,
    As_right: float,
    Mu: float = 0,
    Vu: float = 0
) -> BoundaryZoneCheck:
    """
    Verifica refuerzo en zonas de extremo segun §18.10.2.4.

    Esta verificacion aplica a muros/pilares con:
    - hw/lw >= 2.0 (esbeltos)
    - Seccion critica unica (continuos desde base a tope)

    Requisito (a): rho >= 6*sqrt(f'c)/fy dentro de 0.15*lw del extremo

    Args:
        hw: Altura del muro/pilar (mm)
        lw: Longitud del muro/pilar (mm)
        bw: Espesor del muro/pilar (mm)
        fc: Resistencia del hormigon f'c (MPa)
        fy: Fluencia del acero fy (MPa)
        As_left: Area de acero en extremo izquierdo (mm2)
        As_right: Area de acero en extremo derecho (mm2)
        Mu: Momento ultimo en seccion critica (tonf-m), opcional
        Vu: Cortante ultimo en seccion critica (tonf), opcional

    Returns:
        BoundaryZoneCheck con resultado de la verificacion
    """
    warnings: List[str] = []

    # 1. Verificar aplicabilidad: hw/lw >= 2.0
    hw_lw = hw / lw if lw > 0 else 0
    applies = hw_lw >= 2.0

    # 2. Calcular cuantia minima segun §18.10.2.4(a)
    # rho_min = 6 * sqrt(f'c) / fy con f'c y fy en psi
    fc_psi = fc * MPA_TO_PSI
    fy_psi = fy * MPA_TO_PSI
    rho_min_boundary = 6 * math.sqrt(fc_psi) / fy_psi

    # 3. Calcular zona de extremo: 0.15 * lw
    boundary_length = 0.15 * lw
    boundary_area = boundary_length * bw

    # 4. Calcular cuantias actuales
    if boundary_area > 0:
        rho_actual_left = As_left / boundary_area
        rho_actual_right = As_right / boundary_area
    else:
        rho_actual_left = 0
        rho_actual_right = 0

    # 5. Verificar cuantias
    rho_left_ok = rho_actual_left >= rho_min_boundary
    rho_right_ok = rho_actual_right >= rho_min_boundary

    # 6. Calcular extension vertical segun §18.10.2.4(b)
    # Extension >= max(lw, Mu/(3*Vu))
    if Vu > 0:
        # Mu en tonf-m, Vu en tonf -> resultado en m, convertir a mm
        Mu_3Vu = (Mu / (3 * Vu)) * 1000  # mm
    else:
        Mu_3Vu = 0

    extension_required = max(lw, Mu_3Vu)

    # 7. Determinar resultado global
    if applies:
        is_ok = rho_left_ok and rho_right_ok

        # Generar warnings
        if not rho_left_ok:
            As_req = rho_min_boundary * boundary_area
            warnings.append(
                f"Extremo izquierdo: rho={rho_actual_left:.4f} < "
                f"rho_min={rho_min_boundary:.4f}. "
                f"Requiere As >= {As_req:.0f} mm2 en zona de {boundary_length:.0f}mm"
            )

        if not rho_right_ok:
            As_req = rho_min_boundary * boundary_area
            warnings.append(
                f"Extremo derecho: rho={rho_actual_right:.4f} < "
                f"rho_min={rho_min_boundary:.4f}. "
                f"Requiere As >= {As_req:.0f} mm2 en zona de {boundary_length:.0f}mm"
            )
    else:
        # No aplica: verificacion pasa automaticamente
        is_ok = True
        warnings.append(
            f"§18.10.2.4 no aplica: hw/lw = {hw_lw:.2f} < 2.0"
        )

    return BoundaryZoneCheck(
        hw_lw=round(hw_lw, 2),
        applies=applies,
        rho_min_boundary=round(rho_min_boundary, 5),
        rho_actual_left=round(rho_actual_left, 5),
        rho_actual_right=round(rho_actual_right, 5),
        rho_left_ok=rho_left_ok,
        rho_right_ok=rho_right_ok,
        boundary_length=round(boundary_length, 1),
        boundary_width=round(bw, 1),
        extension_required=round(extension_required, 1),
        lw=round(lw, 1),
        Mu_3Vu=round(Mu_3Vu, 1),
        is_ok=is_ok,
        warnings=warnings,
        aci_reference="ACI 318-25 §18.10.2.4"
    )
