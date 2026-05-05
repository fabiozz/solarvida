"""
Service Layer — Motor de Cálculo Solar (Strategy Pattern)
Responsável pelo processamento do domínio de negócio.
Requisito B2: Validação de inputs (OWASP ASVS V5.1)
"""


class CalculadoraSolar:
    """
    Strategy Pattern: encapsula o algoritmo de dimensionamento fotovoltaico.
    Constantes baseadas em médias brasileiras.
    """
    HORAS_SOL_PICO_DIA = 4.5          # HSP média Brasil Sul
    EFICIENCIA_SISTEMA = 0.75          # perdas típicas (inversores, cabos, sujeira)
    CUSTO_POR_KWP = 5000.00           # R$/kWp instalado (média mercado BR 2024)
    TARIFA_KWEH_MEDIA = 0.75          # R$/kWh (média tarifas distribuidoras)

    # ASVS V5.1 — limites de validação explícitos
    MIN_CONSUMO_KWH = 50.0
    MAX_CONSUMO_KWH = 100_000.0
    MIN_FATURA = 30.0
    MAX_FATURA = 100_000.0

    def validar_inputs(self, consumo_kwh: float, valor_fatura: float):
        """
        Requisito B2 — OWASP ASVS V5.1.3: Validar limites de valores numéricos.
        Lança ValueError com mensagem segura (sem stack trace exposto).
        """
        erros = []
        if not (self.MIN_CONSUMO_KWH <= consumo_kwh <= self.MAX_CONSUMO_KWH):
            erros.append(f"Consumo deve estar entre {self.MIN_CONSUMO_KWH} e {self.MAX_CONSUMO_KWH} kWh.")
        if not (self.MIN_FATURA <= valor_fatura <= self.MAX_FATURA):
            erros.append(f"Valor da fatura deve estar entre R${self.MIN_FATURA} e R${self.MAX_FATURA}.")
        if erros:
            raise ValueError(" | ".join(erros))

    def calcular(self, consumo_kwh: float, valor_fatura: float) -> dict:
        """
        Dimensiona o sistema fotovoltaico e calcula economia.
        Retorna dict com todos os resultados do domínio SimulacaoSolar.
        """
        self.validar_inputs(consumo_kwh, valor_fatura)

        # Dimensionamento do sistema
        consumo_diario = consumo_kwh / 30
        potencia_kwp = consumo_diario / (self.HORAS_SOL_PICO_DIA * self.EFICIENCIA_SISTEMA)
        potencia_kwp = round(potencia_kwp, 2)

        # Economia
        geracao_mensal = potencia_kwp * self.HORAS_SOL_PICO_DIA * 30 * self.EFICIENCIA_SISTEMA
        economia_mensal = min(geracao_mensal * self.TARIFA_KWEH_MEDIA, valor_fatura * 0.95)
        economia_anual = round(economia_mensal * 12, 2)

        # Custo e payback
        custo_sistema = round(potencia_kwp * self.CUSTO_POR_KWP, 2)
        payback_anos = (
            custo_sistema / economia_anual
            if economia_anual > 0 else 0
        )

        return {
            "consumo_mensal_kwh": round(consumo_kwh, 2),
            "valor_fatura_reais": round(valor_fatura, 2),
            "tamanho_sistema_kwp": potencia_kwp,
            "economia_estimada_anual": economia_anual,
            "payback_anos": payback_anos,
            "custo_estimado_sistema": custo_sistema,
        }
        