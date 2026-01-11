# run.py
"""
INGEO Structures - Aplicación de análisis estructural.

Verificación de muros de hormigón armado según ACI 318-25.

Ejecutar con:
    python run.py

Acceder en: http://localhost:5001
"""
import os
import sys

from flask import Flask, render_template, send_from_directory

from app.routes import piers_bp, columns_bp, beams_bp, slabs_bp, drop_beams_bp, common_bp


def create_app() -> Flask:
    """
    Crea la aplicación Flask para análisis estructural.

    Esta aplicación es completamente standalone:
    - No requiere autenticación
    - No requiere base de datos
    - No requiere variables de entorno
    """
    # Obtener rutas de templates y static
    template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'app', 'static')

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )

    # Configuración básica
    app.config['SECRET_KEY'] = 'ingeo-structures-dev-key'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

    # CORS headers para desarrollo
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # Registrar blueprints
    app.register_blueprint(piers_bp)
    app.register_blueprint(columns_bp)
    app.register_blueprint(beams_bp)
    app.register_blueprint(slabs_bp)
    app.register_blueprint(drop_beams_bp)
    app.register_blueprint(common_bp)

    # Ruta principal
    @app.route('/')
    def index():
        """Página principal del módulo estructural."""
        return render_template('structural_standalone.html')

    # Ruta para archivos estáticos
    @app.route('/structural/static/<path:filename>')
    def structural_static(filename):
        return send_from_directory(static_dir, filename)

    # Manejo de errores
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return {'error': 'Archivo demasiado grande. Máximo 50MB.'}, 413

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Error interno del servidor.'}, 500

    return app


def main():
    """Punto de entrada para ejecución directa."""
    app = create_app()

    print("\n" + "="*60)
    print("  INGEO STRUCTURES")
    print("  Verificación de muros según ACI 318-25")
    print("="*60)
    print("\n  Servidor: http://localhost:5001")
    print("  Presiona Ctrl+C para detener\n")

    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )


if __name__ == '__main__':
    main()
