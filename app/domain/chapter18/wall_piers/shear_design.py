# app/domain/chapter18/piers/shear_design.py
"""
Diseño por cortante de pilares de muro según ACI 318-25 §18.10.8.1.

Incluye:
- Cortante de diseño Ve (capacidad o amplificado)
- Verificación de resistencia φVn

Referencias:
- §18.10.8.1(a): Wall piers - cortante según §18.7.6.1 o Ω₀×Vu
- §18.7.6.1: Columnas especiales - Ve basado en Mpr de vigas
"""
from typing import Optional
from ...shear.verification import ShearVerificationService
from ...constants import DCR_MAX_FINITE
from ...constants.shear import PHI_SHEAR_SEISMIC
from ..results import WallPierShearDesign


def calculate_design_shear(
    Vu: float,
    lu: float = 0,
    Mpr_total: Optional[float] = None,
    Mpr_top: float = 0,
    Mpr_bottom: float = 0,
    Omega_o: float = 3.0
) -> WallPierShearDesign:
    """
    Calcula el cortante de diseño Ve según ACI 318-25.

    Aplica diseño por capacidad (§18.7.6.1, §18.10.8.1(a)) cuando hay
    vigas de acople que transmiten momento al elemento.

    Ecuación de diseño por capacidad:
        Ve = Mpr_total / lu  (donde Mpr_total = Mpr_izq + Mpr_der de vigas)

    Con límite superior:
        Ve = min(Ve_capacity, Ω₀ × Vu)

    Args:
        Vu: Cortante del análisis (tonf)
        lu: Altura libre del elemento (mm)
        Mpr_total: Momento probable total de vigas de acople (tonf-m).
                   Si se proporciona, se usa directamente.
                   Si no, se usa Mpr_top + Mpr_bottom.
        Mpr_top: Momento probable en extremo superior (tonf-m)
        Mpr_bottom: Momento probable en extremo inferior (tonf-m)
        Omega_o: Factor de sobrerresistencia (default 3.0 para SFRS)

    Returns:
        WallPierShearDesign con cortante de diseño Ve
    """
    # Determinar Mpr a usar
    if Mpr_total is not None:
        Mpr_sum = Mpr_total
    else:
        Mpr_sum = Mpr_top + Mpr_bottom

    # Determinar si aplica diseño por capacidad
    use_capacity_design = Mpr_sum > 0 and lu > 0

    if use_capacity_design:
        # Ve = Mpr / lu (convertir lu de mm a m)
        lu_m = lu / 1000
        Ve_capacity = Mpr_sum / lu_m
        # Límite superior: Ve <= Ω₀ × Vu
        Ve = min(Ve_capacity, Omega_o * Vu)
    else:
        # Sin vigas de acople: Ve = Vu (del análisis)
        Ve = Vu

    return WallPierShearDesign(
        Vu=Vu,
        Ve=round(Ve, 2),
        Omega_o=Omega_o,
        use_capacity_design=use_capacity_design,
        phi_Vn=0,  # Se llena en verify_shear_strength
        dcr=0,
        is_ok=True,
        aci_reference="ACI 318-25 §18.7.6.1, §18.10.8.1(a)"
    )


def verify_shear_strength(
    Ve: float,
    lw: float,
    bw: float,
    fc: float,
    rho_h: float,
    fyt: float,
    hw: float = 0
) -> WallPierShearDesign:
    """
    Verifica la resistencia al cortante del pilar.

    Delega a ShearVerificationService para el cálculo de Vn.

    Args:
        Ve: Cortante de diseño (tonf)
        lw: Longitud del pilar (mm)
        bw: Espesor del pilar (mm)
        fc: f'c del hormigón (MPa)
        rho_h: Cuantía horizontal
        fyt: Fluencia del refuerzo horizontal (MPa)
        hw: Altura del pilar (mm)

    Returns:
        WallPierShearDesign actualizado con capacidad
    """
    # Usar ShearVerificationService para calcular Vn (instancia local)
    shear_service = ShearVerificationService()
    _Vc, _Vs, Vn, _Vn_max, _alpha_c, _alpha_sh = shear_service.calculate_Vn_wall(
        lw=lw,
        tw=bw,
        hw=hw if hw > 0 else lw,  # Usar lw si no se proporciona hw
        fc=fc,
        fy=fyt,
        rho_h=rho_h
    )

    # φ = 0.60 para wall piers sísmicos especiales (§21.2.4.1)
    phi_Vn = PHI_SHEAR_SEISMIC * Vn

    dcr = Ve / phi_Vn if phi_Vn > 0 else DCR_MAX_FINITE
    is_ok = dcr <= 1.0

    return WallPierShearDesign(
        Vu=0,
        Ve=Ve,
        Omega_o=0,
        use_capacity_design=False,
        phi_Vn=round(phi_Vn, 2),
        dcr=round(dcr, 3),
        is_ok=is_ok,
        aci_reference="ACI 318-25 18.10.4, 18.10.8.1(b)"
    )
