"""
DAO Layer — UsuarioDAO (MVC: Model / DAO Pattern)
Requisito B1: Queries parametrizadas (OWASP ASVS V5.3 / CWE-89 SQL Injection prevention)
"""
import uuid
from datetime import datetime
from models.database import get_connection

class UsuarioDAO:

    def criar(self, nome: str, email: str, senha_hash: str) -> str:
        """Insere novo usuário. Retorna o ID gerado."""
        novo_id = str(uuid.uuid4())
        # ASVS V5.3 — uso de queries parametrizadas, nunca f-string/concatenação
        conn = get_connection()
        conn.execute(
            "INSERT INTO usuarios (id, nome, email, senha_hash) VALUES (?, ?, ?, ?)",
            (novo_id, nome, email, senha_hash)
        )
        conn.commit()
        conn.close()
        return novo_id

    def buscar_por_email(self, email: str):
        """Retorna o usuario dict ou None. Query parametrizada."""
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def buscar_por_id(self, uid: str):
        """Retorna usuario por ID."""
        conn = get_connection()
        row = conn.execute(
            "SELECT id, nome, email, criado_em FROM usuarios WHERE id = ?", (uid,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def incrementar_tentativas(self, email: str):
        """Incrementa contador de tentativas falhas (CWE-307)."""
        conn = get_connection()
        conn.execute(
            "UPDATE usuarios SET tentativas_falhas = tentativas_falhas + 1 WHERE email = ?",
            (email,)
        )
        conn.commit()
        conn.close()

    def bloquear_conta(self, email: str, ate: str):
        """Bloqueia conta até datetime indicado (CWE-307)."""
        conn = get_connection()
        conn.execute(
            "UPDATE usuarios SET bloqueado_ate = ? WHERE email = ?",
            (ate, email)
        )
        conn.commit()
        conn.close()

    def resetar_tentativas(self, email: str):
        """Reseta tentativas após login bem-sucedido."""
        conn = get_connection()
        conn.execute(
            "UPDATE usuarios SET tentativas_falhas = 0, bloqueado_ate = NULL WHERE email = ?",
            (email,)
        )
        conn.commit()
        conn.close()
