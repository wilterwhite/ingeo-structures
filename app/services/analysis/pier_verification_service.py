# app/services/analysis/pier_verification_service.py
"""
Servicio de verificación ACI 318-25 para piers.

Maneja las verificaciones de conformidad con:
- Capítulo 11: Muros (Walls)
- Capítulo 18: Estructuras resistentes a sismos
"""
from typing import Dict, Any, Optional

from ..parsing.session_manager import SessionManager
from .aci_318_25_service import ACI318_25_Service
from ...domain.entities import PierForces
from ...domain.chapter11 import WallType, WallCastType
from ...domain.constants import SeismicDesignCategory


class PierVerificationService:
    """
    Servicio de verificación ACI 318-25 para piers.

    Gestiona la verificación de conformidad con los capítulos 11 y 18
    del código ACI 318-25, manejando la gestión de sesiones.
    """

    def __init__(
        self,
        session_manager: SessionManager,
        aci_318_25_service: Optional[ACI318_25_Service] = None
    ):
        """
        Inicializa el servicio de verificación.

        Args:
            session_manager: Gestor de sesiones (requerido)
            aci_318_25_service: Servicio ACI 318-25 (opcional)
        """
        self._session_manager = session_manager
        self._aci_318_25_service = aci_318_25_service or ACI318_25_Service()

    # =========================================================================
    # Helpers
    # =========================================================================

    def _get_sdc_enum(self, sdc: str) -> SeismicDesignCategory:
        """Convierte string SDC a enum."""
        return {
            'A': SeismicDesignCategory.A,
            'B': SeismicDesignCategory.B,
            'C': SeismicDesignCategory.C,
            'D': SeismicDesignCategory.D,
            'E': SeismicDesignCategory.E,
            'F': SeismicDesignCategory.F
        }.get(sdc.upper(), SeismicDesignCategory.D)

    def _get_wall_type_enum(self, wall_type: str) -> WallType:
        """Convierte string wall_type a enum."""
        return {
            'bearing': WallType.BEARING,
            'nonbearing': WallType.NONBEARING,
            'basement': WallType.BASEMENT,
            'foundation': WallType.FOUNDATION
        }.get(wall_type, WallType.BEARING)

    def _get_max_Vu(self, pier_forces: Optional[PierForces]) -> tuple:
        """Obtiene el cortante máximo de las combinaciones."""
        Vu = 0.0
        Vu_Eh = 0.0
        if pier_forces and pier_forces.combinations:
            for combo in pier_forces.combinations:
                Vu_combo = max(abs(combo.V2), abs(combo.V3))
                if Vu_combo > Vu:
                    Vu = Vu_combo
                    Vu_Eh = Vu_combo
        return Vu, Vu_Eh

    def _get_hwcs_hn(
        self,
        session_id: str,
        pier_key: str,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None
    ) -> tuple:
        """Obtiene hwcs y hn_ft, usando valores calculados si no se proporcionan."""
        if hwcs is None or hwcs <= 0:
            hwcs = self._session_manager.get_hwcs(session_id, pier_key)
        if hn_ft is None or hn_ft <= 0:
            hn_ft = self._session_manager.get_hn_ft(session_id)
        return hwcs, hn_ft

    # =========================================================================
    # Validación
    # =========================================================================

    def _validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Valida que la sesión existe."""
        if not self._session_manager.has_session(session_id):
            return {
                'success': False,
                'error': 'Session not found. Please upload the file again.'
            }
        return None

    def _validate_pier(
        self,
        session_id: str,
        pier_key: str
    ) -> Optional[Dict[str, Any]]:
        """Valida que el pier existe en la sesión."""
        session_error = self._validate_session(session_id)
        if session_error:
            return session_error

        pier = self._session_manager.get_pier(session_id, pier_key)
        if pier is None:
            return {'success': False, 'error': f'Pier not found: {pier_key}'}
        return None

    # =========================================================================
    # Verificación ACI 318-25 Capítulo 11
    # =========================================================================

    def verify_aci_318_25(
        self,
        session_id: str,
        pier_key: str,
        wall_type: str = 'bearing',
        cast_type: str = 'cast_in_place'
    ) -> Dict[str, Any]:
        """
        Verifica conformidad ACI 318-25 Capitulo 11 para un pier.

        Incluye verificaciones de:
        - Espesor minimo (11.3.1)
        - Espaciamiento maximo de refuerzo (11.7)
        - Doble cortina (11.7.2.3)
        - Refuerzo minimo (11.6)
        - Metodo simplificado (11.5.3)
        - Muros esbeltos (11.8)

        Args:
            session_id: ID de sesion
            pier_key: Clave del pier (Story_Label)
            wall_type: Tipo de muro ('bearing', 'nonbearing', 'basement')
            cast_type: Tipo de construccion ('cast_in_place', 'precast')

        Returns:
            Dict con resultados de verificacion ACI 318-25
        """
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        # Convertir tipos
        wall_type_enum = self._get_wall_type_enum(wall_type)
        cast_type_enum = {
            'cast_in_place': WallCastType.CAST_IN_PLACE,
            'precast': WallCastType.PRECAST
        }.get(cast_type, WallCastType.CAST_IN_PLACE)

        # Ejecutar verificacion
        if pier_forces:
            result = self._aci_318_25_service.verify_from_pier_forces(
                pier=pier,
                pier_forces=pier_forces,
                wall_type=wall_type_enum
            )
        else:
            result = self._aci_318_25_service.verify_chapter_11(
                pier=pier,
                wall_type=wall_type_enum,
                cast_type=cast_type_enum
            )

        summary = self._aci_318_25_service.get_verification_summary(result)

        return {
            'success': True,
            'pier_key': pier_key,
            'aci_318_25': summary
        }

    def verify_all_piers_aci_318_25(
        self,
        session_id: str,
        wall_type: str = 'bearing'
    ) -> Dict[str, Any]:
        """
        Verifica conformidad ACI 318-25 para todos los piers de la sesion.

        Args:
            session_id: ID de sesion
            wall_type: Tipo de muro por defecto

        Returns:
            Dict con resultados de verificacion para todos los piers
        """
        error = self._validate_session(session_id)
        if error:
            return error

        parsed_data = self._session_manager.get_session(session_id)

        results = []
        issues_count = 0
        warnings_count = 0
        wall_type_enum = self._get_wall_type_enum(wall_type)

        for key, pier in parsed_data.piers.items():
            pier_forces = parsed_data.pier_forces.get(key)

            if pier_forces:
                result = self._aci_318_25_service.verify_from_pier_forces(
                    pier=pier,
                    pier_forces=pier_forces,
                    wall_type=wall_type_enum
                )
            else:
                result = self._aci_318_25_service.verify_chapter_11(
                    pier=pier,
                    wall_type=wall_type_enum
                )

            self._aci_318_25_service.get_verification_summary(result)
            issues_count += len(result.critical_issues)
            warnings_count += len(result.warnings)

            results.append({
                'pier_key': key,
                'story': pier.story,
                'label': pier.label,
                'all_ok': result.all_ok,
                'critical_issues': result.critical_issues,
                'warnings': result.warnings
            })

        # Estadisticas
        total = len(results)
        ok_count = sum(1 for r in results if r['all_ok'])
        not_ok_count = total - ok_count

        return {
            'success': True,
            'statistics': {
                'total_piers': total,
                'ok': ok_count,
                'not_ok': not_ok_count,
                'total_issues': issues_count,
                'total_warnings': warnings_count,
                'compliance_rate': round(ok_count / total * 100, 1) if total > 0 else 0
            },
            'results': results
        }

    # =========================================================================
    # Verificación ACI 318-25 Capítulo 18 (Sísmico)
    # =========================================================================

    def verify_seismic(
        self,
        session_id: str,
        pier_key: str,
        sdc: str = 'D',
        delta_u: float = 0,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        sigma_max: float = 0,
        is_wall_pier: bool = False
    ) -> Dict[str, Any]:
        """
        Verifica conformidad ACI 318-25 Capitulo 18 para un pier.

        Verifica requisitos sismicos para muros estructurales especiales:
        - Amplificacion de cortante (18.10.3.3)
        - Requisitos de muro especial (18.10.2)
        - Elementos de borde (18.10.6)
        - Pilar de muro (18.10.8)

        Args:
            session_id: ID de sesion
            pier_key: Clave del pier (Story_Label)
            sdc: Categoria de Diseno Sismico ('A', 'B', 'C', 'D', 'E', 'F')
            delta_u: Desplazamiento de diseno en tope (mm)
            hwcs: Altura del muro desde seccion critica (mm), None = usar calculado
            hn_ft: Altura total del edificio (pies), None = usar calculado
            sigma_max: Esfuerzo maximo de compresion (MPa)
            is_wall_pier: Si es un pilar de muro (segmento estrecho)

        Returns:
            Dict con resultados de verificacion sismica
        """
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        # Obtener hwcs/hn_ft calculados si no se proporcionan
        hwcs, hn_ft = self._get_hwcs_hn(session_id, pier_key, hwcs, hn_ft)

        # Convertir SDC y obtener Vu máximo
        sdc_enum = self._get_sdc_enum(sdc)
        Vu, Vu_Eh = self._get_max_Vu(pier_forces)

        # Ejecutar verificacion
        result = self._aci_318_25_service.verify_chapter_18(
            pier=pier,
            sdc=sdc_enum,
            Vu=Vu,
            Vu_Eh=Vu_Eh,
            delta_u=delta_u,
            hwcs=hwcs if hwcs and hwcs > 0 else pier.height,
            hn_ft=hn_ft if hn_ft else 0,
            sigma_max=sigma_max,
            is_wall_pier=is_wall_pier
        )

        summary = self._aci_318_25_service.get_chapter_18_summary(result)

        return {
            'success': True,
            'pier_key': pier_key,
            'chapter_18': summary
        }

    def verify_combined_aci(
        self,
        session_id: str,
        pier_key: str,
        wall_type: str = 'bearing',
        sdc: str = 'D',
        delta_u: float = 0,
        hwcs: Optional[float] = None,
        hn_ft: Optional[float] = None,
        sigma_max: float = 0,
        is_wall_pier: bool = False
    ) -> Dict[str, Any]:
        """
        Verificacion combinada de Capitulos 11 y 18 para un pier.

        Args:
            session_id: ID de sesion
            pier_key: Clave del pier
            wall_type: Tipo de muro
            sdc: Categoria de Diseno Sismico
            delta_u: Desplazamiento de diseno (mm)
            hwcs: Altura desde seccion critica (mm), None = usar calculado
            hn_ft: Altura del edificio (pies), None = usar calculado
            sigma_max: Esfuerzo maximo (MPa)
            is_wall_pier: Si es pilar de muro

        Returns:
            Dict con resultados combinados
        """
        error = self._validate_pier(session_id, pier_key)
        if error:
            return error

        pier = self._session_manager.get_pier(session_id, pier_key)
        pier_forces = self._session_manager.get_pier_forces(session_id, pier_key)

        # Usar helpers para hwcs/hn_ft y SDC
        hwcs, hn_ft = self._get_hwcs_hn(session_id, pier_key, hwcs, hn_ft)
        sdc_enum = self._get_sdc_enum(sdc)

        # Ejecutar verificacion combinada
        result = self._aci_318_25_service.verify_combined(
            pier=pier,
            pier_forces=pier_forces,
            sdc=sdc_enum,
            delta_u=delta_u,
            hwcs=hwcs if hwcs and hwcs > 0 else pier.height,
            hn_ft=hn_ft if hn_ft else 0,
            sigma_max=sigma_max,
            is_wall_pier=is_wall_pier
        )

        return {
            'success': True,
            'pier_key': pier_key,
            **result
        }

    def verify_all_piers_seismic(
        self,
        session_id: str,
        sdc: str = 'D',
        hn_ft: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Verifica conformidad sismica para todos los piers de la sesion.

        Args:
            session_id: ID de sesion
            sdc: Categoria de Diseno Sismico
            hn_ft: Altura del edificio (pies), None = usar calculado

        Returns:
            Dict con resultados para todos los piers
        """
        error = self._validate_session(session_id)
        if error:
            return error

        parsed_data = self._session_manager.get_session(session_id)

        # Usar hn_ft calculado si no se proporciona
        if hn_ft is None or hn_ft <= 0:
            hn_ft = self._session_manager.get_hn_ft(session_id)

        sdc_enum = self._get_sdc_enum(sdc)
        results = []
        issues_count = 0
        warnings_count = 0

        for key, pier in parsed_data.piers.items():
            pier_forces = parsed_data.pier_forces.get(key)

            # Obtener hwcs para este pier
            hwcs = pier.height  # default
            if parsed_data.continuity_info and key in parsed_data.continuity_info:
                hwcs = parsed_data.continuity_info[key].hwcs

            # Obtener cortante maximo
            Vu, Vu_Eh = self._get_max_Vu(pier_forces)

            result = self._aci_318_25_service.verify_chapter_18(
                pier=pier,
                sdc=sdc_enum,
                Vu=Vu,
                Vu_Eh=Vu_Eh,
                hwcs=hwcs,
                hn_ft=hn_ft if hn_ft else 0
            )

            issues_count += len(result.critical_issues)
            warnings_count += len(result.warnings)

            results.append({
                'pier_key': key,
                'story': pier.story,
                'label': pier.label,
                'sdc': result.sdc.value,
                'wall_category': result.wall_category.value,
                'all_ok': result.all_ok,
                'critical_issues': result.critical_issues,
                'warnings': result.warnings
            })

        # Estadisticas
        total = len(results)
        ok_count = sum(1 for r in results if r['all_ok'])
        not_ok_count = total - ok_count

        return {
            'success': True,
            'sdc': sdc,
            'statistics': {
                'total_piers': total,
                'ok': ok_count,
                'not_ok': not_ok_count,
                'total_issues': issues_count,
                'total_warnings': warnings_count,
                'compliance_rate': round(ok_count / total * 100, 1) if total > 0 else 0
            },
            'results': results
        }
