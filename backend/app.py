"""
SolarVida — Aplicação Flask Principal
Arquitetura MVC + DAO + Design Patterns:
  - Singleton: instância única do app Flask e banco de dados
  - Factory: criação de conexões DB via get_connection()
  - Strategy: CalculadoraSolar (algoritmo intercambiável)
  - DAO: acesso a dados desacoplado
  - Observer: AuditDAO registra eventos de segurança

Requisitos de Segurança implementados:
  A1: JWT com assinatura criptográfica + expiração curta (STRIDE Spoofing)
  A2: HTTPS recomendado em produção (STRIDE Tampering)
  A3: Execução sem privilégios elevados
  B1: Queries parametrizadas — CWE-89 (ASVS V5.3)
  B2: Validação de inputs com limites — ASVS V5.1
  B3: Hash bcrypt rounds=12 — ASVS V2.4.1
  C1: Bloqueio após 5 tentativas — CWE-307
  C2: Headers de segurança via Talisman/manual
  C3: IDOR prevention — validação de propriedade no DAO
  C4: Audit log de eventos críticos — não-repúdio
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from models.database import init_db
from controllers.auth_controller import auth_bp
from controllers.simulacao_controller import sim_bp


def create_app() -> Flask:
    """Factory Pattern — cria e configura a aplicação Flask."""
    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = os.environ.get(
        'JWT_SECRET_KEY',
        'solarvida-dev-secret-change-in-production-32chars!'  # em prod: variável de ambiente
    )
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 1800  # 30 minutos (A1)
    app.config['JSON_SORT_KEYS'] = False

    # C2 — Headers de segurança (OWASP ASVS V14.4)
    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Cache-Control'] = 'no-store'
        return response

    # CORS — permite apenas origens confiáveis (em prod, especificar domínios)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    JWTManager(app)

    # Registra blueprints (Controllers)
    app.register_blueprint(auth_bp)
    app.register_blueprint(sim_bp)

    # Rota de health checkss
    @app.route('/api/health')
    def health():
        return jsonify({"status": "ok", "sistema": "SolarVida"}), 200

    # Tratamento de erros genérico — não expõe stack trace (ASVS V7.4.1)
    @app.errorhandler(Exception)
    def handle_error(e):
        code = getattr(e, 'code', 500)
        return jsonify({"erro": "Erro interno. Contate o suporte."}), code

    return app


if __name__ == '__main__':
    init_db()
    app = create_app()
    print("🌞 SolarVida Backend iniciado em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
