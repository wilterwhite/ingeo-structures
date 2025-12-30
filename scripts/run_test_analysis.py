# scripts/run_test_analysis.py
"""
Script para ejecutar análisis de los piers de prueba y mostrar resultados.
"""
import os
import sys
import json

# Agregar el path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pier_analysis import PierAnalysisService


def run_analysis():
    """Ejecuta el análisis de los piers de prueba."""

    # Leer el Excel de prueba
    excel_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "examples",
        "test_data_5piers.xlsx"
    )

    if not os.path.exists(excel_path):
        print(f"Error: No se encontró el archivo {excel_path}")
        print("Ejecute primero: python generate_test_data.py")
        return

    with open(excel_path, "rb") as f:
        file_content = f.read()

    # Crear servicio y analizar
    service = PierAnalysisService()
    session_id = "test-session"

    # Parsear Excel
    print("=" * 70)
    print("ANÁLISIS DE PIERS DE PRUEBA - ACI 318-25")
    print("=" * 70)

    parse_result = service.parse_excel(file_content, session_id)
    if not parse_result.get('success'):
        print(f"Error parseando Excel: {parse_result.get('error')}")
        return

    print(f"\nPiers encontrados: {parse_result.get('n_piers', 0)}")
    print(f"Pisos: {parse_result.get('stories', [])}")

    # Ejecutar análisis completo
    print("\n" + "-" * 70)
    print("RESULTADOS DEL ANÁLISIS")
    print("-" * 70)

    analysis_result = service.analyze(session_id, generate_plots=False)

    if not analysis_result.get('success'):
        print(f"Error en análisis: {analysis_result.get('error')}")
        return

    # Mostrar resultados por pier
    results = analysis_result.get('results', [])

    for r in results:
        geo = r['geometry']
        mat = r['materials']
        cls = r['classification']
        sln = r['slenderness']
        flx = r['flexure']
        shr = r['shear']
        amp = r['shear_amplification']
        bdy = r['boundary_element']

        lw_tw = geo['width_m'] / geo['thickness_m'] if geo['thickness_m'] > 0 else 0

        print(f"\n{'='*60}")
        print(f"PIER: {r['story']} - {r['pier_label']}")
        print(f"Dimensiones: {geo['width_m']:.2f} x {geo['thickness_m']:.2f} m (lw/tw = {lw_tw:.1f})")
        print(f"Altura: {geo['height_m']:.2f} m")
        print(f"f'c: {mat['fc_MPa']} MPa, fy: {mat['fy_MPa']} MPa")
        print(f"{'='*60}")

        # Clasificación
        print(f"\n[CLASIFICACION ACI 318-25 18.10.8]")
        print(f"  Tipo: {cls['type']}")
        print(f"  lw/tw: {cls['lw_tw']:.1f}")
        print(f"  hw/lw: {cls['hw_lw']:.2f}")
        print(f"  Es wall pier: {'Si' if cls['is_wall_pier'] else 'No'}")

        # Esbeltez
        print(f"\n[ESBELTEZ]")
        print(f"  lambda = {sln['lambda']:.1f}")
        print(f"  Es esbelto: {'Si' if sln['is_slender'] else 'No'}")
        if sln['is_slender']:
            print(f"  Factor reduccion: {sln['reduction']:.3f}")

        # Flexocompresión
        print(f"\n[FLEXOCOMPRESION]")
        sf_flx = flx['sf'] if isinstance(flx['sf'], str) else f"{flx['sf']:.2f}"
        print(f"  FS = {sf_flx} -> {flx['status']}")
        print(f"  phiMn = {flx['phi_Mn']:.2f} tonf-m")
        print(f"  Pu = {flx['Pu']:.2f} tonf, Mu = {flx['Mu']:.2f} tonf-m")
        print(f"  Combo critico: {flx['critical_combo']}")

        # Cortante
        print(f"\n[CORTANTE]")
        sf_shr = shr['sf'] if isinstance(shr['sf'], str) else f"{shr['sf']:.2f}"
        print(f"  FS = {sf_shr} -> {shr['status']}")
        print(f"  DCR2 = {shr['dcr_2']:.3f}, DCR3 = {shr['dcr_3']:.3f}")
        print(f"  DCR combinado = {shr['dcr_combined']:.3f}")
        print(f"  phiVn2 = {shr['phi_Vn_2']:.2f} tonf, phiVn3 = {shr['phi_Vn_3']:.2f} tonf")
        print(f"  Vu2 = {shr['Vu_2']:.2f} tonf, Vu3 = {shr['Vu_3']:.2f} tonf")
        print(f"  alphac = {shr['alpha_c']:.2f} (formula: {shr['formula_type']})")

        # Amplificación sísmica
        if amp['applies']:
            print(f"\n[AMPLIFICACION SISMICA 18.10.3.3]")
            print(f"  Omega_v = {amp['omega_v']:.2f}")
            print(f"  omega_v = {amp['omega_v_dyn']:.2f}")
            print(f"  Factor total = {amp['factor']:.2f}")
            print(f"  Ve = {amp['Ve']:.2f} tonf")

        # Elementos de borde
        print(f"\n[ELEMENTOS DE BORDE 18.10.6]")
        print(f"  Requerido: {'Si' if bdy['required'] else 'No'}")
        if bdy['method']:
            print(f"  Metodo: {bdy['method']}")

        # Estado general
        print(f"\n>>> ESTADO GENERAL: {r['overall_status']} <<<")

    # Estadísticas
    stats = analysis_result.get('statistics', {})
    print("\n" + "=" * 70)
    print("RESUMEN ESTADÍSTICO")
    print("=" * 70)
    print(f"Total piers: {stats.get('total', 0)}")
    print(f"OK: {stats.get('ok', 0)}")
    print(f"NO OK: {stats.get('not_ok', 0)}")
    print(f"Tasa de cumplimiento: {stats.get('compliance_rate', 0):.1f}%")

    # Skip detailed ACI verification for now (has bug with double_layer attr)

    # Limpiar sesión
    service.clear_session(session_id)

    print("\n" + "=" * 70)
    print("ANÁLISIS COMPLETADO")
    print("=" * 70)

    return results


if __name__ == "__main__":
    run_analysis()
