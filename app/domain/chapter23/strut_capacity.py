# app/domain/chapter23/strut_capacity.py
"""
Servicio para calculo de capacidad de struts no confinados.

Aplica ACI 318-25 Capitulo 23 para elementos pequenos (<15x15 cm)
que no cumplen requisitos de elementos sismicos convencionales.

Caracteristicas del diagrama P-M simplificado:
- Traccion = 0 (hormigon sin refuerzo efectivo)
- Compresion = phi x Fns = 0.75 x 0.34 x fc' x Acs
- Flexion = Mcr (momento de agrietamiento)
- Curva lineal entre compresion pura y flexion pura

Referencia: ACI 318-25 23.4
"""
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
import math

from ..constants.chapter23 import (
    PHI_STRUT,
    FCE_FACTOR_SMALL_COLUMN,
    BETA_S_SMALL_COLUMN,
    BETA_C_SMALL_COLUMN,
    WHITNEY_FACTOR,
)
from ..constants.units import N_TO_TONF, NMM_TO_TONFM
from ..constants.phi_chapter21 import DCR_MAX_FINITE

if TYPE_CHECKING:
    from ..flexure.interaction_diagram import InteractionPoint


@dataclass
class StrutCapacityResult:
    """
    Resultado de verificacion de strut no confinado con diagrama P-M.

    ACI 318-25 Capitulo 23:
    - Fns = fce x Acs (sin refuerzo de compresion)
    - fce = 0.85 x beta_c x beta_s x fc' = 0.34 x fc'
    - phi = 0.75
    - Mcr = fr x S (momento de agrietamiento)
    """
    # Geometria
    Acs: float              # Area de la seccion (mm2)
    b: float                # Ancho de la seccion (mm)
    h: float                # Altura de la seccion (mm)
    fc: float               # f'c del concreto (MPa)

    # Coeficientes (23.4.3)
    beta_s: float           # Coeficiente del strut (0.4)
    beta_c: float           # Factor de confinamiento (1.0)
    fce: float              # Resistencia efectiva (MPa)

    # Capacidades - Compresion (23.4.1a)
    Fns: float              # Resistencia nominal a compresion (tonf)
    phi_Fns: float          # Resistencia de diseno a compresion (tonf)

    # Capacidades - Flexion (19.2.3)
    fr: float               # Modulo de rotura (MPa)
    Mcr: float              # Momento de agrietamiento (tonf-m)
    phi_Mcr: float          # Momento de agrietamiento de diseno (tonf-m)

    # Demandas
    Pu: float               # Carga axial factorizada (tonf)
    Mu: float               # Momento factorizado (tonf-m)

    # Verificacion
    dcr: float              # Demand/Capacity ratio (flexocompresion)
    dcr_P: float            # DCR solo axial
    dcr_M: float            # DCR solo momento
    is_ok: bool             # True si dcr <= 1.0

    # Diagrama
    diagram_points: List['InteractionPoint'] = field(default_factory=list)

    # Metadata
    warnings: List[str] = field(default_factory=list)
    aci_reference: str = "ACI 318-25 23.4"


class StrutCapacityService:
    """
    Servicio para verificar capacidad de elementos pequenos como struts.

    ACI 318-25 Capitulo 23:
    - Fns = fce x Acs (23.4.1a)
    - fce = 0.85 x beta_c x beta_s x fc' (23.4.3)
    - phi = 0.75 (23.3.1)
    - Mcr = fr x S donde fr = 0.62 x sqrt(fc') (19.2.3)

    Para elementos pequenos sin refuerzo transversal:
    - beta_s = 0.4 (conservador, sin refuerzo distribuido)
    - beta_c = 1.0 (sin confinamiento)
    - La barra central NO cuenta como As' de compresion
    - La barra central NO cuenta para resistencia a flexion
    """

    def verify_strut(
        self,
        Acs: float,          # Area de la seccion (mm2)
        fc: float,           # f'c (MPa)
        Pu: float,           # Carga axial factorizada (tonf)
        Mu: float = 0.0,     # Momento factorizado (tonf-m)
        *,
        b: Optional[float] = None,   # Ancho (mm) - para calcular Mcr
        h: Optional[float] = None,   # Altura (mm) - para calcular Mcr
        beta_s: float = BETA_S_SMALL_COLUMN,
        beta_c: float = BETA_C_SMALL_COLUMN,
        sdc: str = "C",      # Seismic Design Category
        lambda_factor: float = 1.0,  # Factor hormigon liviano
    ) -> StrutCapacityResult:
        """
        Verifica capacidad de strut no confinado con diagrama P-M.

        Args:
            Acs: Area de la seccion transversal (mm2)
            fc: Resistencia del concreto (MPa)
            Pu: Carga axial factorizada (tonf, positivo=compresion)
            Mu: Momento factorizado (tonf-m)
            b: Ancho de la seccion (mm), si None se calcula de sqrt(Acs)
            h: Altura de la seccion (mm), si None se calcula de sqrt(Acs)
            beta_s: Coeficiente del strut (default 0.4)
            beta_c: Factor de confinamiento (default 1.0)
            sdc: Categoria de diseno sismico (A, B, C, D, E, F)
            lambda_factor: Factor para hormigon liviano (1.0 = normal)

        Returns:
            StrutCapacityResult con la verificacion completa
        """
        warnings = []

        # Si no se dan dimensiones, asumir seccion cuadrada
        if b is None:
            b = math.sqrt(Acs)
        if h is None:
            h = math.sqrt(Acs)

        # Warning especial para SDC D/E/F
        if sdc.upper() in ('D', 'E', 'F'):
            warnings.append(
                "STRUT SISMICO: Agrietar rigidez 90%, rotular extremos, "
                "arriostrar pandeo en toda altura dentro del plano (Ej: Muros ICF)"
            )

        # =====================================================================
        # 1. Calcular resistencia a compresion (23.4)
        # =====================================================================
        # fce = 0.85 x beta_c x beta_s x fc'
        fce = WHITNEY_FACTOR * beta_c * beta_s * fc  # MPa

        # Fns = fce x Acs (N)
        Fns_N = fce * Acs  # N
        Fns_tonf = Fns_N / N_TO_TONF  # tonf

        # phi_Fns = phi x Fns
        phi_Fns_tonf = PHI_STRUT * Fns_tonf

        # =====================================================================
        # 2. Calcular resistencia a flexion - momento de agrietamiento (19.2.3)
        # =====================================================================
        # fr = 0.62 x lambda x sqrt(fc') en MPa
        fr = 0.62 * lambda_factor * math.sqrt(fc)

        # S = b x h^2 / 6 (modulo de seccion elastico)
        S = b * h**2 / 6  # mm3

        # Mcr = fr x S
        Mcr_Nmm = fr * S  # N-mm
        Mcr_tonfm = Mcr_Nmm / NMM_TO_TONFM  # tonf-m

        # phi_Mcr = phi x Mcr
        phi_Mcr_tonfm = PHI_STRUT * Mcr_tonfm

        # =====================================================================
        # 3. Generar diagrama de interaccion simplificado
        # =====================================================================
        from ..flexure.interaction_diagram import (
            InteractionDiagramService,
            InteractionPoint
        )
        diagram_service = InteractionDiagramService()
        diagram_points = diagram_service.generate_strut_interaction_curve(
            width=h,
            thickness=b,
            fc=fc,
            lambda_factor=lambda_factor,
            n_points=10
        )

        # =====================================================================
        # 4. Calcular DCR de flexocompresion
        # =====================================================================
        Pu_abs = abs(Pu)
        Mu_abs = abs(Mu)

        # DCR individual
        dcr_P = Pu_abs / phi_Fns_tonf if phi_Fns_tonf > 0 else DCR_MAX_FINITE
        dcr_M = Mu_abs / phi_Mcr_tonfm if phi_Mcr_tonfm > 0 else DCR_MAX_FINITE

        # DCR combinado (linea recta en diagrama P-M)
        # El diagrama es triangular: (0, phi_Fns) - (phi_Mcr, 0) - (0, 0)
        # Ecuacion de la linea: P/phi_Fns + M/phi_Mcr = 1
        dcr = self._calculate_dcr_from_diagram(
            Pu_abs, Mu_abs, phi_Fns_tonf, phi_Mcr_tonfm
        )

        is_ok = dcr <= 1.0

        # =====================================================================
        # 5. Warnings
        # =====================================================================
        # Warning si Pu negativo (traccion) - falla pero mostramos DCR real
        if Pu < 0:
            warnings.append(
                f"TRACCION: Pu={Pu:.2f}t < 0, hormigon no armado no resiste traccion"
            )
            # NO sobrescribir dcr con 100 - mantener valor real para información
            is_ok = False

        # Warning si DCR alto
        if dcr > 0.67 and dcr <= 1.0:
            warnings.append(
                f"DCR={dcr:.2f} > 0.67: Factor de seguridad bajo ({1/dcr:.2f})"
            )

        if not is_ok and Pu >= 0:  # Solo mostrar si no es por tracción
            warnings.append(
                f"Capacidad insuficiente: DCR={dcr:.2f} > 1.0"
            )

        # Info sobre tipo de elemento
        warnings.insert(0, "Elemento tratado como strut no confinado (Cap. 23)")
        warnings.insert(1, "La barra se considera constructiva - no aporta capacidad")

        return StrutCapacityResult(
            Acs=round(Acs, 0),
            b=round(b, 1),
            h=round(h, 1),
            fc=round(fc, 1),
            beta_s=beta_s,
            beta_c=beta_c,
            fce=round(fce, 2),
            Fns=round(Fns_tonf, 2),
            phi_Fns=round(phi_Fns_tonf, 2),
            fr=round(fr, 2),
            Mcr=round(Mcr_tonfm, 4),
            phi_Mcr=round(phi_Mcr_tonfm, 4),
            Pu=round(Pu_abs, 2),
            Mu=round(Mu_abs, 4),
            dcr=round(dcr, 3),
            dcr_P=round(dcr_P, 3),
            dcr_M=round(dcr_M, 3),
            is_ok=is_ok,
            diagram_points=diagram_points,
            warnings=warnings,
        )

    def _calculate_dcr_from_diagram(
        self,
        Pu: float,
        Mu: float,
        phi_Fns: float,
        phi_Mcr: float
    ) -> float:
        """
        Calcula DCR contra el diagrama P-M triangular simplificado.

        El diagrama tiene 3 vertices:
        - (0, phi_Fns): Compresion pura
        - (phi_Mcr, 0): Flexion pura
        - (0, 0): Origen (traccion = 0)

        La linea de capacidad es: P/phi_Fns + M/phi_Mcr = 1

        Args:
            Pu: Carga axial (tonf)
            Mu: Momento (tonf-m)
            phi_Fns: Capacidad a compresion (tonf)
            phi_Mcr: Capacidad a momento (tonf-m)

        Returns:
            DCR = distancia al origen / distancia a la linea de capacidad
        """
        # Caso trivial: sin carga
        if Pu <= 0 and Mu <= 0:
            return 0.0

        # Caso solo compresion
        if Mu <= 1e-6:
            return Pu / phi_Fns if phi_Fns > 0 else DCR_MAX_FINITE

        # Caso solo momento
        if Pu <= 1e-6:
            return Mu / phi_Mcr if phi_Mcr > 0 else DCR_MAX_FINITE

        # Caso general: flexocompresion
        # La capacidad en la direccion (Pu, Mu) es el punto de interseccion
        # con la linea P/phi_Fns + M/phi_Mcr = 1
        #
        # El punto de demanda (Pu, Mu) esta en la direccion del rayo desde el origen.
        # El punto de capacidad (Pc, Mc) esta en la linea y satisface:
        #   Mc/Mu = Pc/Pu = k (factor de escala)
        #   Pc/phi_Fns + Mc/phi_Mcr = 1
        #   k*Pu/phi_Fns + k*Mu/phi_Mcr = 1
        #   k = 1 / (Pu/phi_Fns + Mu/phi_Mcr)
        #
        # DCR = 1/k = Pu/phi_Fns + Mu/phi_Mcr
        dcr = Pu / phi_Fns + Mu / phi_Mcr

        return dcr
