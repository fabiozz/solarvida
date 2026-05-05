"""
Controller Layer — AuthController (MVC: Controller)
Requisitos de segurança implementados:
  B1: SQL Injection prevention (queries parametrizadas via DAO)
  B3: Hash de senhas com bcrypt (OWASP ASVS V2.4.1)
  C1: Bloqueio de conta após 5 tentativas (CWE-307)
  A1: JWT com expiração curta (STRIDE Spoofing mitigation)
"""
import bcrypt
import re
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from models.usuario_dao import UsuarioDAO
from models.audit_dao import AuditDAO

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
usuario_dao = UsuarioDAO()
audit_dao = AuditDAO()

MAX_TENTATIVAS = 5
BLOQUEIO_MINUTOS = 15

# Requisito B3 — Regex de complexidade de senha (OWASP ASVS V2.1.1)
SENHA_REGEX = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
)
EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _ip():
    return request.remote_addr or "unknown"


@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    """T2 — Cadastro de usuário com validação e hash de senha."""
    data = request.get_json(silent=True) or {}

    nome = str(data.get('nome', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    senha = str(data.get('senha', ''))

    # Validações de formato — B2 (ASVS V5.1)
    erros = []
    if not nome or len(nome) < 2:
        erros.append("Nome deve ter ao menos 2 caracteres.")
    if not EMAIL_REGEX.match(email):
        erros.append("E-mail inválido.")
    if not SENHA_REGEX.match(senha):
        erros.append(
            "Senha deve ter ≥ 8 caracteres, maiúscula, minúscula, número e símbolo (@$!%*?&)."
        )
    if erros:
        return jsonify({"erro": " | ".join(erros)}), 400

    # Verifica duplicidade
    if usuario_dao.buscar_por_email(email):
        return jsonify({"erro": "E-mail já cadastrado."}), 409

    # B3 — bcrypt com work factor 12 (ASVS V2.4.1)
    hash_senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt(rounds=12)).decode()
    uid = usuario_dao.criar(nome, email, hash_senha)

    audit_dao.registrar("CADASTRO", uid, _ip(), f"Novo usuário: {email}")
    return jsonify({"mensagem": "Usuário criado com sucesso.", "id": uid}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """T3 — Autenticação com JWT e bloqueio por tentativas (CWE-307)."""
    data = request.get_json(silent=True) or {}
    email = str(data.get('email', '')).strip().lower()
    senha = str(data.get('senha', ''))

    usuario = usuario_dao.buscar_por_email(email)

    if not usuario:
        # Mensagem genérica — não revela se email existe (ASVS V2.2.1)
        audit_dao.registrar("LOGIN_FALHA", None, _ip(), f"Email não encontrado: {email}")
        return jsonify({"erro": "Credenciais inválidas."}), 401

    # C1 — Verifica bloqueio temporal (CWE-307)
    if usuario.get('bloqueado_ate'):
        bloqueado_ate = datetime.fromisoformat(usuario['bloqueado_ate'])
        if datetime.now(timezone.utc).replace(tzinfo=None) < bloqueado_ate:
            minutos = int((bloqueado_ate - datetime.utcnow()).total_seconds() / 60) + 1
            return jsonify({"erro": f"Conta bloqueada. Tente novamente em {minutos} minuto(s)."}), 429

    # Verifica senha
    if not bcrypt.checkpw(senha.encode(), usuario['senha_hash'].encode()):
        usuario_dao.incrementar_tentativas(email)
        tentativas = usuario['tentativas_falhas'] + 1
        audit_dao.registrar("LOGIN_FALHA", usuario['id'], _ip(), f"Senha incorreta. Tentativa {tentativas}")

        if tentativas >= MAX_TENTATIVAS:
            ate = (datetime.utcnow() + timedelta(minutes=BLOQUEIO_MINUTOS)).isoformat()
            usuario_dao.bloquear_conta(email, ate)
            audit_dao.registrar("CONTA_BLOQUEADA", usuario['id'], _ip(),
                                f"Bloqueada por {BLOQUEIO_MINUTOS}min")
            return jsonify({"erro": f"Conta bloqueada por {BLOQUEIO_MINUTOS} minutos."}), 429

        restantes = MAX_TENTATIVAS - tentativas
        return jsonify({"erro": f"Credenciais inválidas. {restantes} tentativa(s) restante(s)."}), 401

    # Login bem-sucedido
    usuario_dao.resetar_tentativas(email)
    # A1 — JWT com expiração curta (30 minutos) — STRIDE Spoofing mitigation
    token = create_access_token(
        identity=usuario['id'],
        expires_delta=timedelta(minutes=30)
    )
    audit_dao.registrar("LOGIN_SUCESSO", usuario['id'], _ip())
    return jsonify({
        "token": token,
        "nome": usuario['nome'],
        "email": usuario['email']
    }), 200


@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    """Retorna dados do usuário autenticado."""
    uid = get_jwt_identity()
    usuario = usuario_dao.buscar_por_id(uid)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado."}), 404
    return jsonify(usuario), 200
    