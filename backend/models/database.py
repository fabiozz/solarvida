"""
Model Layer — Database initialization and schema (MVC: Model)
Padrão: DAO (Data Access Object)
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'solarvida.db')


def get_connection():
    """Factory para conexões SQLite com configurações seguras."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Cria as tabelas se não existirem."""
    conn = get_connection()
    cur = conn.cursor()

    # Tabela de usuários
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id          TEXT PRIMARY KEY,
            nome        TEXT NOT NULL,
            email       TEXT NOT NULL UNIQUE,
            senha_hash  TEXT NOT NULL,
            criado_em   TEXT NOT NULL DEFAULT (datetime('now')),
            tentativas_falhas INTEGER NOT NULL DEFAULT 0,
            bloqueado_ate     TEXT
        )
    """)

    # Tabela de simulações (domínio principal)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS simulacoes (
            id                      TEXT PRIMARY KEY,
            usuario_id              TEXT NOT NULL,
            consumo_mensal_kwh      REAL NOT NULL,
            valor_fatura_reais      REAL NOT NULL,
            tamanho_sistema_kwp     REAL NOT NULL,
            economia_estimada_anual REAL NOT NULL,
            payback_anos            REAL NOT NULL,
            custo_estimado_sistema  REAL NOT NULL,
            data_simulacao          TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # Tabela de audit log (Requisito de segurança: Auditoria / Repudiação)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id         TEXT PRIMARY KEY,
            usuario_id TEXT,
            acao       TEXT NOT NULL,
            ip         TEXT,
            detalhes   TEXT,
            criado_em  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    