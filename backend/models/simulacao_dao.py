"""
DAO Layer — SimulacaoDAO (MVC: Model / DAO Pattern)
Entidade principal do domínio: SimulacaoSolar
"""
import uuid
from models.database import get_connection


class SimulacaoDAO:
    """DAO para operações CRUD da entidade SimulacaoSolar."""

    def criar(self, usuario_id: str, consumo_kwh: float, valor_fatura: float,
              tamanho_kwp: float, economia_anual: float, payback: float,
              custo_sistema: float) -> str:
        novo_id = str(uuid.uuid4())
        conn = get_connection()
        conn.execute("""
            INSERT INTO simulacoes
              (id, usuario_id, consumo_mensal_kwh, valor_fatura_reais,
               tamanho_sistema_kwp, economia_estimada_anual, payback_anos,
               custo_estimado_sistema)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (novo_id, usuario_id, consumo_kwh, valor_fatura,
              tamanho_kwp, economia_anual, payback, custo_sistema))
        conn.commit()
        conn.close()
        return novo_id

    def listar_por_usuario(self, usuario_id: str):
        """Lista todas as simulações do usuário autenticado."""
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM simulacoes
            WHERE usuario_id = ?
            ORDER BY data_simulacao DESC
        """, (usuario_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def buscar_por_id(self, sim_id: str, usuario_id: str):
        """Busca simulação garantindo que pertence ao usuário (IDOR prevention)."""
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM simulacoes WHERE id = ? AND usuario_id = ?",
            (sim_id, usuario_id)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def deletar(self, sim_id: str, usuario_id: str) -> bool:
        """Remove simulação. Verifica propriedade antes de deletar."""
        conn = get_connection()
        cur = conn.execute(
            "DELETE FROM simulacoes WHERE id = ? AND usuario_id = ?",
            (sim_id, usuario_id)
        )
        conn.commit()
        conn.close()
        return cur.rowcount > 0
        