# app/domain/entities/verification_result.py
"""
Entidad VerificationResult: resultado de la verificación estructural de un pier.

Incluye verificaciones ACI 318-25:
- Flexocompresión (Capítulo 22)
- Cortante (Capítulos 11 y 18)
- Clasificación de muros (§18.10.8)
- Amplificación de cortante (§18.10.3.3)
- Elementos de borde (§18.10.6)
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class VerificationResult:
    """
    Resultado de la verificación estructural de un pier.
    """
    pier_label: str
    story: str

    # Datos del pier
    width_m: float          # m
    thickness_m: float      # m
    height_m: float         # m
    fc_MPa: float
    fy_MPa: float
    As_vertical_mm2: float
    As_horizontal_mm2: float
    rho_vertical: float
    rho_horizontal: float

    # Resultados de flexocompresión
    flexure_sf: float           # Factor de seguridad (>=1 OK)
    flexure_status: str         # "OK" o "NO OK"
    critical_combo_flexure: str # Combinación crítica
    flexure_phi_Mn_0: float     # Capacidad φMn a P=0, flexión pura (tonf-m)
    flexure_phi_Mn_at_Pu: float # Capacidad φMn a Pu crítico (tonf-m)
    flexure_Pu: float           # Carga axial crítica (tonf)
    flexure_Mu: float           # Momento crítico (tonf-m)

    # Resultados de corte con interacción V2-V3 (caso crítico entre combinaciones)
    shear_sf: float             # Factor de seguridad combinado = 1/DCR
    shear_status: str           # "OK" o "NO OK"
    critical_combo_shear: str   # Combinación crítica
    shear_dcr_2: float          # Demand/Capacity ratio V2 = Vu2/φVn2
    shear_dcr_3: float          # Demand/Capacity ratio V3 = Vu3/φVn3
    shear_dcr_combined: float   # DCR combinado = dcr_2 + dcr_3
    shear_phi_Vn_2: float       # Resistencia de diseño V2 (tonf)
    shear_phi_Vn_3: float       # Resistencia de diseño V3 (tonf)
    shear_Vu_2: float           # Demanda V2 (tonf)
    shear_Vu_3: float           # Demanda V3 (tonf)
    shear_Vc: float             # Contribución del hormigón (tonf)
    shear_Vs: float             # Contribución del acero (tonf)
    shear_alpha_c: float        # Coeficiente αc usado
    shear_formula_type: str     # "wall" o "column"

    # Resumen
    overall_status: str         # "OK" o "NO OK"

    # Diseño por capacidad (§18.10.8.1(a), §18.7.6.1)
    shear_Ve: float = 0.0                    # Cortante de diseño Ve = Mpr/lu (tonf)
    shear_uses_capacity_design: bool = False # Si usa diseño por capacidad

    # Esbeltez (campos con defaults al final)
    slenderness_lambda: float = 0.0     # Ratio de esbeltez k*lu/r
    slenderness_is_slender: bool = False  # True si lambda > 22
    slenderness_reduction: float = 1.0  # Factor de reduccion por pandeo

    # Tracción
    flexure_exceeds_axial: bool = False  # Si Pu > φPn,max
    flexure_phi_Pn_max: float = 0.0      # Capacidad axial máxima (tonf)
    flexure_has_tension: bool = False    # Si hay combinaciones con Pu < 0
    flexure_tension_combos: int = 0      # Número de combos con tracción

    # Gráfico (opcional)
    pm_plot_base64: str = ""

    # ==========================================================================
    # Clasificación de muros (ACI 318-25 §18.10.8)
    # ==========================================================================
    classification_type: str = ""           # column, wall, wall_pier_column, etc
    classification_lw_tw: float = 0.0       # Relación lw/tw
    classification_hw_lw: float = 0.0       # Relación hw/lw
    classification_aci_section: str = ""    # Sección ACI aplicable
    classification_is_wall_pier: bool = False  # Si es pilar de muro

    # ==========================================================================
    # Amplificación de cortante (ACI 318-25 §18.10.3.3)
    # ==========================================================================
    amplification_omega_v: float = 1.0      # Factor Ωv de sobrerresistencia
    amplification_omega_v_dyn: float = 1.0  # Factor ωv dinámico
    amplification_factor: float = 1.0       # Factor total Ωv × ωv
    amplification_Ve: float = 0.0           # Cortante amplificado Ve (tonf)
    amplification_applies: bool = False     # Si aplica amplificación

    # ==========================================================================
    # Elementos de borde (ACI 318-25 §18.10.6)
    # ==========================================================================
    boundary_required: bool = False         # Si requiere elemento de borde
    boundary_method: str = ""               # stress o displacement
    boundary_sigma_max: float = 0.0         # Esfuerzo máximo (MPa)
    boundary_limit: float = 0.0             # Límite 0.2*f'c (MPa)
    boundary_length_mm: float = 0.0         # Extensión horizontal (mm)
    boundary_aci_reference: str = ""        # Referencia ACI

    # ==========================================================================
    # Continuidad del muro (para §18.10.3.3 y §18.10.6)
    # ==========================================================================
    continuity_hwcs_m: float = 0.0          # hwcs en metros
    continuity_n_stories: int = 1           # Número de pisos del muro continuo
    continuity_is_continuous: bool = False  # Si el muro continúa a otros pisos
    continuity_is_base: bool = True         # Si es la base del muro continuo
    continuity_hwcs_lw: float = 0.0         # Relación hwcs/lw

    # ==========================================================================
    # Propuesta de diseño (cuando falla verificación)
    # ==========================================================================
    has_proposal: bool = False              # Si tiene propuesta de diseño
    proposal_failure_mode: str = ""         # flexure, shear, combined, slenderness
    proposal_type: str = ""                 # boundary_bars, mesh, thickness, combined
    proposal_description: str = ""          # Descripción corta de la propuesta
    proposal_sf_original: float = 0.0       # SF original (antes de propuesta)
    proposal_sf_proposed: float = 0.0       # SF propuesto (después de propuesta)
    proposal_dcr_original: float = 0.0      # DCR original (antes de propuesta)
    proposal_dcr_proposed: float = 0.0      # DCR propuesto (después de propuesta)
    proposal_success: bool = False          # Si la propuesta resuelve el problema
    proposal_changes: str = ""              # Cambios específicos (ej: "4φ16 borde")
    proposed_config: Optional[Dict[str, Any]] = field(default=None)  # Config para preview

    # ==========================================================================
    # Exceso de capacidad axial (campos al final por orden de dataclass)
    # ==========================================================================
    flexure_exceeds_axial: bool = False  # Si Pu > φPn,max (excede capacidad axial)
    flexure_phi_Pn_max: float = 0.0      # Capacidad axial máxima φPn,max (tonf)

    @property
    def is_ok(self) -> bool:
        return self.overall_status == "OK"

    def _format_sf(self, value: float) -> Any:
        """Formatea un factor de seguridad para la API."""
        if value >= 100:
            return '>100'
        return round(value, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario para la API."""
        return {
            'pier_label': self.pier_label,
            'story': self.story,
            'geometry': {
                'width_m': self.width_m,
                'thickness_m': self.thickness_m,
                'height_m': self.height_m
            },
            'materials': {
                'fc_MPa': self.fc_MPa,
                'fy_MPa': self.fy_MPa
            },
            'reinforcement': {
                'As_vertical_mm2': self.As_vertical_mm2,
                'As_horizontal_mm2': self.As_horizontal_mm2,
                'rho_vertical': round(self.rho_vertical, 5),
                'rho_horizontal': round(self.rho_horizontal, 5)
            },
            'slenderness': {
                'lambda': round(self.slenderness_lambda, 1),
                'is_slender': self.slenderness_is_slender,
                'reduction': round(self.slenderness_reduction, 3),
                'reduction_pct': round((1 - self.slenderness_reduction) * 100, 0)
            },
            # Clasificación ACI 318-25 §18.10.8
            'classification': {
                'type': self.classification_type,
                'lw_tw': round(self.classification_lw_tw, 2),
                'hw_lw': round(self.classification_hw_lw, 2),
                'aci_section': self.classification_aci_section,
                'is_wall_pier': self.classification_is_wall_pier
            },
            'flexure': {
                'sf': self._format_sf(self.flexure_sf),
                'status': self.flexure_status,
                'critical_combo': self.critical_combo_flexure,
                'phi_Mn_0': round(self.flexure_phi_Mn_0, 1),       # Capacidad a P=0
                'phi_Mn_at_Pu': round(self.flexure_phi_Mn_at_Pu, 1),  # Capacidad a Pu crítico
                'Pu': round(self.flexure_Pu, 1),
                'Mu': round(self.flexure_Mu, 1),
                'exceeds_axial': self.flexure_exceeds_axial,      # Si Pu > φPn,max
                'phi_Pn_max': round(self.flexure_phi_Pn_max, 1),  # Capacidad axial máxima
                'has_tension': self.flexure_has_tension,          # Si hay combinaciones con tracción
                'tension_combos': self.flexure_tension_combos     # Número de combos con tracción
            },
            'shear': {
                'sf': self._format_sf(self.shear_sf),
                'status': self.shear_status,
                'critical_combo': self.critical_combo_shear,
                'dcr_2': round(self.shear_dcr_2, 3),
                'dcr_3': round(self.shear_dcr_3, 3),
                'dcr_combined': round(self.shear_dcr_combined, 3),
                'phi_Vn_2': round(self.shear_phi_Vn_2, 1),
                'phi_Vn_3': round(self.shear_phi_Vn_3, 1),
                'Vu_2': round(self.shear_Vu_2, 1),
                'Vu_3': round(self.shear_Vu_3, 1),
                'Ve': round(self.shear_Ve, 2),
                'uses_capacity_design': self.shear_uses_capacity_design,
                'Vc': round(self.shear_Vc, 2),
                'Vs': round(self.shear_Vs, 2),
                'alpha_c': round(self.shear_alpha_c, 3),
                'formula_type': self.shear_formula_type
            },
            # Amplificación de cortante ACI 318-25 §18.10.3.3
            'shear_amplification': {
                'omega_v': round(self.amplification_omega_v, 3),
                'omega_v_dyn': round(self.amplification_omega_v_dyn, 3),
                'factor': round(self.amplification_factor, 3),
                'Ve': round(self.amplification_Ve, 2),
                'applies': self.amplification_applies
            },
            # Elementos de borde ACI 318-25 §18.10.6
            'boundary_element': {
                'required': self.boundary_required,
                'method': self.boundary_method,
                'sigma_max_MPa': round(self.boundary_sigma_max, 2),
                'limit_MPa': round(self.boundary_limit, 2),
                'length_mm': round(self.boundary_length_mm, 0),
                'aci_reference': self.boundary_aci_reference
            },
            # Continuidad del muro
            'wall_continuity': {
                'hwcs_m': round(self.continuity_hwcs_m, 2),
                'hwcs_lw': round(self.continuity_hwcs_lw, 2),
                'n_stories': self.continuity_n_stories,
                'is_continuous': self.continuity_is_continuous,
                'is_base': self.continuity_is_base
            },
            'overall_status': self.overall_status,
            'pm_plot': self.pm_plot_base64,
            # Propuesta de diseño
            'design_proposal': {
                'has_proposal': self.has_proposal,
                'failure_mode': self.proposal_failure_mode,
                'proposal_type': self.proposal_type,
                'description': self.proposal_description,
                'sf_original': round(self.proposal_sf_original, 3),
                'sf_proposed': round(self.proposal_sf_proposed, 3),
                'dcr_original': round(self.proposal_dcr_original, 3),
                'dcr_proposed': round(self.proposal_dcr_proposed, 3),
                'success': self.proposal_success,
                'changes': self.proposal_changes,
                'proposed_config': self.proposed_config  # Config para preview de sección
            } if self.has_proposal else None
        }
