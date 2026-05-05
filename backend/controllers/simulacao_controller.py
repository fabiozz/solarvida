"""
Controller Layer — SimulacaoController (MVC: Controller)
T4 — CRUD da entidade principal SimulacaoSolar
Requisito B2: Validação de inputs via CalculadoraSolar (ASVS V5.1)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.simulacao_dao import SimulacaoDAO
from models.audit_dao import AuditDAO
from services.calculadora_solar import CalculadoraSolar

sim_bp = Blueprint('simulacoes', __name__, url_prefix='/api/simulacoes')
simulacao_dao = SimulacaoDAO()
audit_dao = AuditDAO()
calculadora = CalculadoraSolar()


def _ip():
    return request.remote_addr or "unknown"

@sim_bp.route('/calcular', methods=['POST'])
@jwt_required()
def calcular_simulacao():
    data = request.get_json() or {}

    try:
        consumo = float(data['consumo_mensal_kwh'])
        fatura = float(data['valor_fatura_reais'])
    except:
        return jsonify({"erro": "Entrada inválida"}), 400

    resultado = calculadora.calcular(consumo, fatura)

    return jsonify(resultado), 200

@sim_bp.route('', methods=['POST'])
@jwt_required()
def salvar_simulacao():
    uid = get_jwt_identity()
    data = request.get_json() or {}

    sim_id = simulacao_dao.criar(
        usuario_id=uid,
        consumo_kwh=data['consumo_mensal_kwh'],
        valor_fatura=data['valor_fatura_reais'],
        tamanho_kwp=data['tamanho_sistema_kwp'],
        economia_anual=data['economia_estimada_anual'],
        payback=data['payback_anos'],
        custo_sistema=data['custo_estimado_sistema'],
    )

    audit_dao.registrar("SIMULACAO_CRIADA", uid, _ip(), f"ID: {sim_id}")

    return jsonify({"id": sim_id}), 201


@sim_bp.route('', methods=['GET'])
@jwt_required()
def listar_simulacoes():
    """Lista simulações do usuário autenticado."""
    uid = get_jwt_identity()
    sims = simulacao_dao.listar_por_usuario(uid)
    return jsonify(sims), 200


@sim_bp.route('/<sim_id>', methods=['GET'])
@jwt_required()
def buscar_simulacao(sim_id):
    """Busca simulação por ID — verifica propriedade (IDOR prevention)."""
    uid = get_jwt_identity()
    sim = simulacao_dao.buscar_por_id(sim_id, uid)
    if not sim:
        return jsonify({"erro": "Simulação não encontrada."}), 404
    return jsonify(sim), 200


@sim_bp.route('/<sim_id>', methods=['DELETE'])
@jwt_required()
def deletar_simulacao(sim_id):
    """Remove simulação verificando propriedade."""
    uid = get_jwt_identity()
    removido = simulacao_dao.deletar(sim_id, uid)
    if not removido:
        return jsonify({"erro": "Simulação não encontrada."}), 404
    audit_dao.registrar("SIMULACAO_REMOVIDA", uid, _ip(), f"ID: {sim_id}")
    return jsonify({"mensagem": "Simulação removida."}), 200
