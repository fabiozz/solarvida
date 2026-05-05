"""
DAO Layer — AuditDAO (Requisito A1 / R-Repudiation mitigation)
Registra todas as ações relevantes de segurança.
"""
import uuid
from models.database import get_connection

class AuditDAO:

    def registrar(self, acao: str, usuario_id: str = None,
                  ip: str = None, detalhes: str = None):
        log_id = str(uuid.uuid4())
        conn = get_connection()
        conn.execute("""
            INSERT INTO audit_log (id, usuario_id, acao, ip, detalhes)
            VALUES (?, ?, ?, ?, ?)
        """, (log_id, usuario_id, acao, ip, detalhes))
        conn.commit()
        conn.close()

