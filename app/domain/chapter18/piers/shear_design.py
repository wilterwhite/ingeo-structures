# app/domain/chapter18/piers/shear_design.py
"""
Diseño por cortante de pilares de muro según ACI 318-25 §18.10.8.1.

Incluye:
- Cortante de diseño Ve (capacidad o amplificado)
- Verificación de resistencia φVn
"""
from ...shear.verification import ShearVerificationService
from ...constants.shear import PHI_SHEAR
from ..results import WallPierShearDesign


def calculate_design_shear(
    Vu: float,
    use_capacity_design: bool = True,
    Mpr_top: float = 0,
    Mpr_bottom: float = 0,
    lu: float = 0,
    Omega_o: float = 3.0
) -> WallPierShearDesign:
    """
    Calcula el cortante de diseño para el pilar.

    Según 18.10.8.1(a):
    - Cortante según 18.7.6.1 (diseño por capacidad), O
    - Ve <= Omega_o * Vu del análisis

    Para 18.7.6.1:
    Ve = (Mpr_top + Mpr_bottom) / lu

    Args:
        Vu: Cortante del análisis (tonf)
        use_capacity_design: Si usar diseño por capacidad
        Mpr_top: Momento probable en extremo superior (tonf-m)
        Mpr_bottom: Momento probable en extremo inferior (tonf-m)
        lu: Altura libre del pilar (mm)
        Omega_o: Factor de sobrerresistencia del código general

    Returns:
        WallPierShearDesign con cortante de diseño
    """
    if use_capacity_design and lu > 0:
        # Diseño por capacidad: Ve = (Mpr_top + Mpr_bottom) / lu
        # Convertir lu a m para unidades consistentes
        lu_m = lu / 1000
        Ve_capacity = (Mpr_top + Mpr_bottom) / lu_m
        Ve = min(Ve_capacity, Omega_o * Vu)
    else:
        # Alternativa: Ve = Omega_o * Vu
        Ve = Omega_o * Vu

    return WallPierShearDesign(
        Vu=Vu,
        Ve=round(Ve, 2),
        Omega_o=Omega_o,
        use_capacity_design=use_capacity_design,
        phi_Vn=0,  # Se llena después
        dcr=0,
        is_ok=True,
        aci_reference="ACI 318-25 18.10.8.1(a), 18.7.6.1"
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
    _Vc, _Vs, Vn, _Vn_max, _alpha_c = shear_service.calculate_Vn_wall(
        lw=lw,
        tw=bw,
        hw=hw if hw > 0 else lw,  # Usar lw si no se proporciona hw
        fc=fc,
        fy=fyt,
        rho_h=rho_h
    )

    phi_Vn = PHI_SHEAR * Vn

    dcr = Ve / phi_Vn if phi_Vn > 0 else float('inf')
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
