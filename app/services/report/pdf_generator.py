# app/services/report/pdf_generator.py
"""
Generador de informes PDF para verificacion estructural ACI 318-25.
"""
import io
import base64
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from reportlab.lib import colors

logger = logging.getLogger(__name__)
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable

from .report_config import ReportConfig


class PDFReportGenerator:
    """
    Generador de informes PDF para verificacion estructural.

    Genera informes completos con:
    - Portada y resumen ejecutivo
    - Piers criticos por carga y cuantia
    - Piers que fallan verificacion
    - Tabla completa de resultados
    - Diagramas P-M (opcional)
    - Secciones transversales (opcional)
    """

    # Colores corporativos
    PRIMARY_COLOR = colors.HexColor('#2563eb')
    SUCCESS_COLOR = colors.HexColor('#16a34a')
    WARNING_COLOR = colors.HexColor('#ca8a04')
    DANGER_COLOR = colors.HexColor('#dc2626')
    GRAY_LIGHT = colors.HexColor('#f3f4f6')
    GRAY_DARK = colors.HexColor('#374151')

    def __init__(self):
        """Inicializa el generador."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos personalizados."""
        # Titulo principal
        self.styles.add(ParagraphStyle(
            name='TitleMain',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.PRIMARY_COLOR,
            alignment=TA_CENTER,
            spaceAfter=20
        ))

        # Subtitulo
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=self.GRAY_DARK,
            alignment=TA_CENTER,
            spaceAfter=10
        ))

        # Encabezado de seccion
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.PRIMARY_COLOR,
            spaceBefore=20,
            spaceAfter=10
        ))

        # Texto normal centrado
        self.styles.add(ParagraphStyle(
            name='CenteredText',
            parent=self.styles['Normal'],
            alignment=TA_CENTER
        ))

        # Estadistica grande
        self.styles.add(ParagraphStyle(
            name='StatLarge',
            parent=self.styles['Normal'],
            fontSize=36,
            alignment=TA_CENTER,
            textColor=self.PRIMARY_COLOR
        ))

        # Estadistica label
        self.styles.add(ParagraphStyle(
            name='StatLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=self.GRAY_DARK
        ))

    def generate_report(
        self,
        results: List[Dict[str, Any]],
        piers: Dict[str, Any],
        config: ReportConfig,
        statistics: Optional[Dict[str, Any]] = None,
        summary_plot_base64: Optional[str] = None
    ) -> bytes:
        """
        Genera el informe PDF completo.

        Args:
            results: Lista de resultados de verificacion (dicts de to_dict())
            piers: Diccionario de piers
            config: Configuracion del informe
            statistics: Estadisticas del analisis
            summary_plot_base64: Grafico resumen en base64 (opcional)

        Returns:
            Bytes del PDF generado
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Construir el contenido
        story = []

        # 1. Portada
        story.extend(self._build_cover_page(config))
        story.append(PageBreak())

        # 2. Resumen ejecutivo
        story.extend(self._build_executive_summary(results, statistics, summary_plot_base64))
        story.append(PageBreak())

        # 3. Piers criticos por carga
        if config.top_by_load > 0:
            story.extend(self._build_critical_by_load(results, config.top_by_load))

        # 4. Piers criticos por cuantia
        if config.top_by_cuantia > 0:
            story.extend(self._build_critical_by_cuantia(results, config.top_by_cuantia))

        # 5. Piers que fallan
        if config.include_failing:
            story.extend(self._build_failing_piers(results, config.include_proposals))

        # 6. Tabla completa
        if config.include_full_table:
            story.append(PageBreak())
            story.extend(self._build_full_results_table(results))

        # 7. Diagramas P-M (recolectar de los resultados si tienen)
        if config.include_pm_diagrams:
            pm_plots = {
                f"{r['story']}_{r['pier_label']}": r.get('pm_plot', '')
                for r in results if r.get('pm_plot')
            }
            if pm_plots:
                story.append(PageBreak())
                story.extend(self._build_pm_diagrams_section(pm_plots, results))

        # Generar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _build_cover_page(self, config: ReportConfig) -> List:
        """Construye la portada del informe."""
        elements = []

        elements.append(Spacer(1, 2*inch))

        # Titulo
        elements.append(Paragraph(
            "Informe de Verificacion Estructural",
            self.styles['TitleMain']
        ))
        elements.append(Paragraph(
            "Segun ACI 318-25",
            self.styles['Subtitle']
        ))

        elements.append(Spacer(1, 0.5*inch))

        # Linea decorativa
        elements.append(HRFlowable(
            width="50%",
            thickness=2,
            color=self.PRIMARY_COLOR,
            spaceBefore=10,
            spaceAfter=30
        ))

        # Nombre del proyecto
        elements.append(Paragraph(
            f"<b>Proyecto:</b> {config.project_name}",
            self.styles['Subtitle']
        ))

        elements.append(Spacer(1, 0.3*inch))

        # Fecha
        fecha = config.generated_at.strftime("%d de %B de %Y") if config.generated_at else ""
        elements.append(Paragraph(
            f"<b>Fecha:</b> {fecha}",
            self.styles['CenteredText']
        ))

        elements.append(Spacer(1, 2*inch))

        # Pie de portada
        elements.append(Paragraph(
            "Generado con INGEO Structures",
            self.styles['CenteredText']
        ))

        return elements

    def _build_executive_summary(
        self,
        results: List[Dict[str, Any]],
        statistics: Optional[Dict[str, Any]],
        summary_plot: Optional[str]
    ) -> List:
        """Construye el resumen ejecutivo."""
        elements = []

        elements.append(Paragraph("Resumen Ejecutivo", self.styles['SectionHeader']))

        # Usar estadisticas proporcionadas o calcular
        if statistics:
            total = statistics.get('total', len(results))
            ok = statistics.get('ok', 0)
            fail = statistics.get('fail', 0)
            pass_rate = statistics.get('pass_rate', 0)
        else:
            total = len(results)
            ok = sum(1 for r in results if r.get('overall_status') == 'OK')
            fail = total - ok
            pass_rate = (ok / total * 100) if total > 0 else 0

        # Tabla de estadisticas
        stats_data = [
            ['Total Piers', 'Aprueban (OK)', 'Fallan (NO OK)', 'Tasa de Aprobacion'],
            [str(total), str(ok), str(fail), f'{pass_rate:.1f}%']
        ]

        stats_table = Table(stats_data, colWidths=[1.5*inch]*4)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 15),
            ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#dcfce7')),  # Verde claro OK
            ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#fee2e2')),  # Rojo claro FAIL
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('BOX', (0, 0), (-1, -1), 2, self.PRIMARY_COLOR),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))

        # Grafico resumen
        if summary_plot:
            elements.append(Paragraph(
                "<b>Grafico Resumen de Factores de Seguridad</b>",
                self.styles['CenteredText']
            ))
            elements.append(Spacer(1, 0.1*inch))

            try:
                img_data = base64.b64decode(summary_plot)
                img = Image(io.BytesIO(img_data), width=6*inch, height=3*inch)
                elements.append(img)
            except Exception as e:
                logger.warning("Error decodificando gráfico resumen: %s", e)
                elements.append(Paragraph(
                    "(Grafico no disponible)",
                    self.styles['CenteredText']
                ))

        return elements

    def _build_critical_by_load(
        self,
        results: List[Dict[str, Any]],
        n: int
    ) -> List:
        """Construye seccion de piers criticos por carga axial."""
        elements = []

        elements.append(Paragraph(
            f"Piers Criticos por Carga Axial (Top {n})",
            self.styles['SectionHeader']
        ))

        # Ordenar por carga axial (|Pu|) descendente
        def get_pu(r):
            flexure = r.get('flexure', {})
            pu = flexure.get('Pu', 0)
            return abs(pu) if pu else 0

        sorted_results = sorted(results, key=get_pu, reverse=True)[:n]

        if not sorted_results:
            elements.append(Paragraph("No hay datos disponibles.", self.styles['Normal']))
            return elements

        # Construir tabla
        data = [['Piso', 'Pier', 'Pu (tonf)', 'Mu (tonf-m)', 'SF Flex', 'SF Corte', 'Estado']]

        for r in sorted_results:
            flexure = r.get('flexure', {})
            shear = r.get('shear', {})

            sf_flex = flexure.get('sf', 0)
            sf_flex_str = f'{sf_flex:.2f}' if isinstance(sf_flex, (int, float)) and sf_flex < 100 else str(sf_flex)

            sf_shear = shear.get('sf', 0)
            sf_shear_str = f'{sf_shear:.2f}' if isinstance(sf_shear, (int, float)) and sf_shear < 100 else str(sf_shear)

            pu = flexure.get('Pu', 0)
            mu = flexure.get('Mu', 0)

            data.append([
                r.get('story', ''),
                r.get('pier_label', ''),
                f'{abs(pu):.1f}' if pu else '-',
                f'{abs(mu):.1f}' if mu else '-',
                sf_flex_str,
                sf_shear_str,
                r.get('overall_status', '')
            ])

        table = self._create_data_table(data)
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _build_critical_by_cuantia(
        self,
        results: List[Dict[str, Any]],
        n: int
    ) -> List:
        """Construye seccion de piers criticos por cuantia."""
        elements = []

        elements.append(Paragraph(
            f"Piers Criticos por Cuantia Vertical (Top {n})",
            self.styles['SectionHeader']
        ))

        # Ordenar por cuantia vertical descendente
        def get_rho_v(r):
            reinf = r.get('reinforcement', {})
            return reinf.get('rho_vertical', 0) or 0

        sorted_results = sorted(results, key=get_rho_v, reverse=True)[:n]

        if not sorted_results:
            elements.append(Paragraph("No hay datos disponibles.", self.styles['Normal']))
            return elements

        # Construir tabla
        data = [['Piso', 'Pier', 'rho_v (%)', 'rho_h (%)', 'As (mm2)', 'SF', 'Estado']]

        for r in sorted_results:
            reinf = r.get('reinforcement', {})
            flexure = r.get('flexure', {})
            shear = r.get('shear', {})

            rho_v = reinf.get('rho_vertical', 0)
            rho_h = reinf.get('rho_horizontal', 0)
            as_v = reinf.get('As_vertical_mm2', 0)

            sf_flex = flexure.get('sf', 100)
            sf_shear = shear.get('sf', 100)
            # Handle string SF values like '>100'
            if isinstance(sf_flex, str):
                sf_flex = 100
            if isinstance(sf_shear, str):
                sf_shear = 100
            sf_min = min(sf_flex, sf_shear)
            sf_str = f'{sf_min:.2f}' if sf_min < 100 else '>100'

            data.append([
                r.get('story', ''),
                r.get('pier_label', ''),
                f'{rho_v*100:.3f}' if rho_v else '-',
                f'{rho_h*100:.3f}' if rho_h else '-',
                f'{as_v:.0f}' if as_v else '-',
                sf_str,
                r.get('overall_status', '')
            ])

        table = self._create_data_table(data)
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _build_failing_piers(
        self,
        results: List[Dict[str, Any]],
        include_proposals: bool
    ) -> List:
        """Construye seccion de piers que fallan."""
        elements = []

        elements.append(Paragraph(
            "Piers que No Pasan Verificacion",
            self.styles['SectionHeader']
        ))

        # Filtrar piers que fallan
        failing = [r for r in results if r.get('overall_status') != 'OK']

        if not failing:
            elements.append(Paragraph(
                "Todos los piers pasan la verificacion.",
                self.styles['Normal']
            ))
            return elements

        elements.append(Paragraph(
            f"Se encontraron {len(failing)} pier(s) que no cumplen los criterios de verificacion:",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1*inch))

        # Construir tabla
        if include_proposals:
            data = [['Piso', 'Pier', 'SF Flex', 'DCR Corte', 'Modo Falla', 'Propuesta']]
        else:
            data = [['Piso', 'Pier', 'SF Flex', 'SF Corte', 'Combo Critico']]

        for r in failing:
            flexure = r.get('flexure', {})
            shear = r.get('shear', {})
            proposal = r.get('proposal', {})

            sf_flex = flexure.get('sf', 0)
            sf_flex_str = f'{sf_flex:.2f}' if isinstance(sf_flex, (int, float)) and sf_flex < 100 else str(sf_flex)

            sf_shear = shear.get('sf', 0)
            sf_shear_str = f'{sf_shear:.2f}' if isinstance(sf_shear, (int, float)) and sf_shear < 100 else str(sf_shear)

            dcr = shear.get('dcr_combined', 0)

            if include_proposals:
                has_proposal = proposal.get('has_proposal', False)
                modo = proposal.get('failure_mode', '-') if has_proposal else '-'
                desc = proposal.get('description', '-') or '-'
                propuesta = desc[:30] + '...' if len(desc) > 30 else desc
                data.append([
                    r.get('story', ''),
                    r.get('pier_label', ''),
                    sf_flex_str,
                    f'{dcr:.2f}' if dcr else '-',
                    modo,
                    propuesta
                ])
            else:
                data.append([
                    r.get('story', ''),
                    r.get('pier_label', ''),
                    sf_flex_str,
                    sf_shear_str,
                    flexure.get('critical_combo', '-')
                ])

        table = self._create_data_table(data, highlight_status=False)
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _build_full_results_table(self, results: List[Dict[str, Any]]) -> List:
        """Construye la tabla completa de resultados."""
        elements = []

        elements.append(Paragraph(
            "Tabla Completa de Resultados",
            self.styles['SectionHeader']
        ))

        if not results:
            elements.append(Paragraph("No hay resultados.", self.styles['Normal']))
            return elements

        # Tabla con columnas esenciales (cabe en una pagina)
        data = [[
            'Piso', 'Pier', 'Ancho\n(m)', 'Esp.\n(m)', "f'c\n(MPa)",
            'rho_v\n(%)', 'SF\nFlex', 'DCR\nCorte', 'Estado'
        ]]

        for r in results:
            geo = r.get('geometry', {})
            mats = r.get('materials', {})
            reinf = r.get('reinforcement', {})
            flexure = r.get('flexure', {})
            shear = r.get('shear', {})

            sf_flex = flexure.get('sf', 0)
            sf_flex_str = f'{sf_flex:.2f}' if isinstance(sf_flex, (int, float)) and sf_flex < 100 else str(sf_flex)

            dcr = shear.get('dcr_combined', 0)
            rho_v = reinf.get('rho_vertical', 0)

            data.append([
                r.get('story', ''),
                r.get('pier_label', ''),
                f"{geo.get('width_m', 0):.2f}",
                f"{geo.get('thickness_m', 0):.2f}",
                f"{mats.get('fc_MPa', 0):.0f}",
                f'{rho_v*100:.2f}' if rho_v else '-',
                sf_flex_str,
                f'{dcr:.2f}' if dcr else '-',
                r.get('overall_status', '')
            ])

        # Dividir en paginas si hay muchos resultados
        rows_per_page = 30
        for i in range(0, len(data)-1, rows_per_page):
            page_data = [data[0]] + data[i+1:i+1+rows_per_page]
            table = self._create_data_table(page_data, col_widths=[
                0.8*inch, 0.7*inch, 0.6*inch, 0.6*inch, 0.5*inch,
                0.6*inch, 0.5*inch, 0.6*inch, 0.6*inch
            ])
            elements.append(table)
            if i + rows_per_page < len(data) - 1:
                elements.append(PageBreak())

        return elements

    def _build_pm_diagrams_section(
        self,
        pm_plots: Dict[str, str],
        results: List[Dict[str, Any]]
    ) -> List:
        """Construye seccion de diagramas P-M."""
        elements = []

        elements.append(Paragraph(
            "Diagramas de Interaccion P-M",
            self.styles['SectionHeader']
        ))

        elements.append(Paragraph(
            "Diagramas de capacidad (curva) vs demanda (puntos) para los piers criticos.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Crear mapa de resultados para obtener info del pier
        results_map = {
            f"{r.get('story', '')}_{r.get('pier_label', '')}": r
            for r in results
        }

        count = 0
        for pier_key, plot_base64 in pm_plots.items():
            if not plot_base64:
                continue

            if count > 0 and count % 2 == 0:
                elements.append(PageBreak())

            result = results_map.get(pier_key, {})
            label = f"{result.get('story', '')} - {result.get('pier_label', '')}" if result else pier_key

            elements.append(Paragraph(f"<b>{label}</b>", self.styles['Normal']))

            try:
                img_data = base64.b64decode(plot_base64)
                img = Image(io.BytesIO(img_data), width=5.5*inch, height=3.5*inch)
                elements.append(img)
            except Exception as e:
                logger.warning("Error decodificando diagrama P-M para '%s': %s", pier_key, e)
                elements.append(Paragraph("(Diagrama no disponible)", self.styles['Normal']))

            elements.append(Spacer(1, 0.2*inch))
            count += 1

        return elements

    def _build_sections_section(
        self,
        section_diagrams: Dict[str, str],
        results: List[Dict[str, Any]]
    ) -> List:
        """Construye seccion de secciones transversales."""
        elements = []

        elements.append(Paragraph(
            "Secciones Transversales",
            self.styles['SectionHeader']
        ))

        elements.append(Paragraph(
            "Detalle de armadura para los piers criticos.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))

        results_map = {
            f"{r.get('story', '')}_{r.get('pier_label', '')}": r
            for r in results
        }

        count = 0
        for pier_key, diagram_base64 in section_diagrams.items():
            if not diagram_base64:
                continue

            if count > 0 and count % 2 == 0:
                elements.append(PageBreak())

            result = results_map.get(pier_key, {})
            label = f"{result.get('story', '')} - {result.get('pier_label', '')}" if result else pier_key

            elements.append(Paragraph(f"<b>{label}</b>", self.styles['Normal']))

            try:
                img_data = base64.b64decode(diagram_base64)
                img = Image(io.BytesIO(img_data), width=4*inch, height=3*inch)
                elements.append(img)
            except Exception as e:
                logger.warning("Error decodificando diagrama de sección para '%s': %s", pier_key, e)
                elements.append(Paragraph("(Seccion no disponible)", self.styles['Normal']))

            elements.append(Spacer(1, 0.2*inch))
            count += 1

        return elements

    def _create_data_table(
        self,
        data: List[List[str]],
        col_widths: Optional[List[float]] = None,
        highlight_status: bool = True
    ) -> Table:
        """
        Crea una tabla de datos con estilo consistente.

        Args:
            data: Datos de la tabla (primera fila es header)
            col_widths: Anchos de columna opcionales
            highlight_status: Resaltar columna de estado con colores

        Returns:
            Tabla formateada
        """
        table = Table(data, colWidths=col_widths)

        style_commands = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('BOX', (0, 0), (-1, -1), 1, self.PRIMARY_COLOR),
            # Filas alternas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.GRAY_LIGHT]),
        ]

        # Colorear columna de estado si existe
        if highlight_status and len(data) > 1 and len(data[0]) > 0:
            # Buscar columna 'Estado'
            header = data[0]
            estado_col = None
            for i, h in enumerate(header):
                if 'Estado' in str(h):
                    estado_col = i
                    break

            if estado_col is not None:
                for row_idx in range(1, len(data)):
                    cell_value = data[row_idx][estado_col]
                    if cell_value == 'OK':
                        style_commands.append(
                            ('BACKGROUND', (estado_col, row_idx), (estado_col, row_idx),
                             colors.HexColor('#dcfce7'))
                        )
                        style_commands.append(
                            ('TEXTCOLOR', (estado_col, row_idx), (estado_col, row_idx),
                             self.SUCCESS_COLOR)
                        )
                    elif cell_value in ['NO OK', 'FAIL']:
                        style_commands.append(
                            ('BACKGROUND', (estado_col, row_idx), (estado_col, row_idx),
                             colors.HexColor('#fee2e2'))
                        )
                        style_commands.append(
                            ('TEXTCOLOR', (estado_col, row_idx), (estado_col, row_idx),
                             self.DANGER_COLOR)
                        )

        table.setStyle(TableStyle(style_commands))
        return table
