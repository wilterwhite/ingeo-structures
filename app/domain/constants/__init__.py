# app/domain/constants/__init__.py
"""
Constantes ACI 318-25 para diseño estructural.

Módulos:
- units: Constantes de conversión de unidades
- phi_chapter21: Factores de reducción de resistencia (Cap. 21)
- shear: Constantes para verificación de cortante
- seismic: Categorías de diseño sísmico
- materials: Grados de acero y propiedades de materiales
- stiffness: Factores de rigidez efectiva (Tabla 6.6.3.1.1)
"""
from .units import (
    N_TO_TONF, TONF_TO_N,
    NMM_TO_TONFM, TONFM_TO_NMM,
    MM_TO_M, M_TO_MM, MM_TO_FT, INCH_TO_MM,
)
from .phi_chapter21 import (
    PHI_COMPRESSION,
    PHI_COMPRESSION_SPIRAL,
    PHI_TENSION,
    PHI_SHEAR,
    PHI_TORSION,
    PHI_BEARING,
    PHI_SHEAR_SEISMIC,
    PHI_SHEAR_DIAGONAL,
    EPSILON_TY,
    EPSILON_T_LIMIT,
    calculate_phi_flexure,
)
from .shear import (
    # Coeficientes alpha_c para muros
    ALPHA_C_SQUAT,
    ALPHA_C_SLENDER,
    HW_LW_SQUAT_LIMIT,
    HW_LW_SLENDER_LIMIT,
    ALPHA_C_TENSION_STRESS_MPA,
    # Límites de Vn
    VN_MAX_INDIVIDUAL_COEF,
    VN_MAX_GROUP_COEF,
    VC_COEF_COLUMN,
    VS_MAX_COEF,
    # Factor alpha_sh (§18.10.4.4)
    ALPHA_SH_MIN,
    ALPHA_SH_MAX,
    ALPHA_SH_COEF,
    calculate_alpha_sh,
    # Clasificación
    ASPECT_RATIO_WALL_LIMIT,
    DEFAULT_COVER_MM,
    # Wall piers
    WALL_PIER_HW_LW_LIMIT,
    WALL_PIER_COLUMN_LIMIT,
    WALL_PIER_ALTERNATE_LIMIT,
    # Amplificación de cortante
    OMEGA_V_MIN,
    OMEGA_V_MAX,
    OMEGA_V_DYN_COEF,
    OMEGA_V_DYN_BASE,
    OMEGA_V_DYN_MIN,
    OMEGA_0_DEFAULT,
    # Elementos de borde
    BOUNDARY_STRESS_REQUIRED,
    BOUNDARY_STRESS_DISCONTINUE,
    BOUNDARY_DRIFT_MIN,
    BOUNDARY_DRIFT_CAPACITY_MIN,
    BOUNDARY_MIN_WIDTH_RATIO,
    BOUNDARY_MIN_WIDTH_INCHES,
    BOUNDARY_C_LW_THRESHOLD,
    BOUNDARY_SPACING,
    # Fricción por cortante
    SHEAR_FRICTION_MU,
    SHEAR_FRICTION_VN_MAX_COEF_1,
    SHEAR_FRICTION_VN_MAX_COEF_2_BASE,
    SHEAR_FRICTION_VN_MAX_COEF_2_FC,
    SHEAR_FRICTION_VN_MAX_LIMIT_MPa,
    SHEAR_FRICTION_VN_MAX_OTHER_MPa,
    SHEAR_FRICTION_FY_LIMIT_MPa,
    PHI_SHEAR_FRICTION,
)
from .seismic import SeismicDesignCategory, WallCategory, SDC_REQUIREMENTS
from .materials import (
    SteelGrade,
    LAMBDA_NORMAL,
    LAMBDA_SAND_LIGHTWEIGHT,
    LAMBDA_ALL_LIGHTWEIGHT,
    BAR_AREAS,
    AVAILABLE_DIAMETERS,
    get_bar_area,
    # Límites de materiales (§18.2)
    FC_MAX_SHEAR_MPA,
    FC_MAX_LIGHTWEIGHT_MPA,
    FYT_MAX_SHEAR_MPA,
    FYT_MAX_CONFINEMENT_MPA,
    get_effective_fc_shear,
    get_effective_fyt_shear,
    get_effective_fyt_confinement,
    # Propiedades del acero (§20.2)
    ES_MPA,
    EPSILON_CU,
    # Propiedades del concreto (§19.2)
    calculate_Ec,
    calculate_fr,
    # Bloque de Whitney (§22.2.2.4.3)
    calculate_beta1,
)
from .stiffness import (
    WALL_STIFFNESS_FACTOR,
    WALL_UNCRACKED_STIFFNESS_FACTOR,
    COLUMN_STIFFNESS_FACTOR,
    BEAM_STIFFNESS_FACTOR,
    FLAT_SLAB_STIFFNESS_FACTOR,
    M2_MIN_ECCENTRICITY_BASE,
    M2_MIN_ECCENTRICITY_FACTOR,
    SECOND_ORDER_LIMIT,
    CM_BASE,
    CM_FACTOR,
    CM_MIN,
    CM_TRANSVERSE,
)
from .reinforcement import (
    # Constantes
    RHO_MIN,
    FY_DEFAULT_MPA,
    COVER_DEFAULT_PIER_MM,
    COVER_DEFAULT_COLUMN_MM,
    COVER_DEFAULT_BEAM_MM,
    # Funciones
    check_rho_vertical_ge_horizontal,
    is_rho_v_ge_rho_h_required,
)
