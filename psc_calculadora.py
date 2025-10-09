#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculadora de atualização de Precatório (modelo EC-136/25)
- Antes da formação:  IPCA-E + 6% a.a. (≈ 0,5% a.m.)
- Período de graça:   apenas IPCA-E
- Após o grace:       IPCA-E + 2% a.a.

Você fornece:
- valores de entrada (principal, honorários, pagamento de superpreferência, etc.)
- datas (formação do precatório, vencimento, pagamento)
- séries mensais de IPCA-E (lista de frações por mês) para cada etapa
- alíquotas (IR sobre juros, FGTS/Assistência opcionais)

Saídas:
- Tabela com componentes (principal atualizado, juros anteriores/posteriores),
- IR calculado (se incide),
- Valor bruto e líquido, seguindo a lógica mostrada na UI.

OBS: Ajuste as políticas conforme sua sentença/tribunal (juros base mês vs. ano, índices alternativos etc.).
"""

from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
from datetime import date

getcontext().prec = 28  # boa precisão para composições

TWOPLACES = Decimal("0.01")

def D(x) -> Decimal:
    """Atalho seguro para Decimal a partir de int/float/str."""
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x))

def quantize_cents(x: Decimal) -> Decimal:
    return x.quantize(TWOPLACES, rounding=ROUND_HALF_EVEN)

# ---------- util de tempo ----------

def months_between(d1: date, d2: date) -> int:
    """Número de meses completos entre d1 (inclui) e d2 (exclui o mês final se dia<dia inicial).
    Ex.: 2024-01-15 → 2024-03-15 = 2 meses; 15→14 reduz um mês."""
    if d2 < d1:
        return -months_between(d2, d1)
    y = d2.year - d1.year
    m = d2.month - d1.month
    months = y * 12 + m
    if d2.day < d1.day:
        months -= 1
    return months

def annual_to_monthly_rate(annual_rate: Decimal) -> Decimal:
    """Converte juros ao ano para equivalente mensal composto: (1+a)^(1/12)-1."""
    # (1 + a)**(1/12) - 1
    a = D(annual_rate)
    # usar power decimal via float é ok aqui pela precisão escolhida; para 0.02 e 0.06 é suficiente:
    monthly = (Decimal((1 + float(a)) ** (1/12)) - 1)
    return monthly

def compose_factors(ipca_series: list[Decimal], extra_monthly_rate: Decimal = D(0)) -> Decimal:
    """
    Multiplica (1 + ipca_m + extra) mês a mês.
    - ipca_series: lista de frações mensais, e.g., 0.0035 para 0,35%
    - extra_monthly_rate: fração mensal de juros (0.005 = 0,5% a.m.)
    Retorna o fator total composto (>= 1).
    """
    total = Decimal("1")
    for ipm in ipca_series:
        total *= (Decimal("1") + D(ipm) + D(extra_monthly_rate))
    return total

# ---------- dados de entrada ----------

@dataclass
class CalcParams:
    # Valores
    valor_precatorio: Decimal           # "Valor de Face" (base do principal)
    principal: Decimal                  # valor do principal na sentença (sem honorários)
    honorarios_percent: Decimal = D(0)  # se quiser destacar honorários contratuais (% do principal)
    pago_superpreferencia: Decimal = D(0)  # valor já pago (abate após atualização)
    incide_ir: bool = False
    ir_rate: Decimal = D(0)             # ex.: 0.15 (15%) — aplica só sobre juros de mora

    # Datas (ajuste conforme seu processo)
    dt_formacao: date = date(2024, 1, 1)
    dt_vencimento: date = date(2025, 1, 1)   # fim do grace
    dt_pagamento: date = date(2025, 6, 1)

    # Políticas de juros anuais
    juros_aa_antes_formacao: Decimal = D("0.06")  # 6% a.a.
    juros_aa_pos_grace: Decimal = D("0.02")       # 2% a.a.

    # Índices (listas com 1 valor por mês do intervalo correspondente)
    ipca_antes_formacao: list[Decimal] = None
    ipca_grace: list[Decimal] = None
    ipca_pos_grace: list[Decimal] = None

# ---------- motor do cálculo ----------

@dataclass
class CalcResult:
    # Componentes intermediárias (para exibir em tabela)
    principal_atualizado: Decimal
    juros_mora_antes: Decimal
    juros_mora_posteriores: Decimal

    # Totais e bases
    valor_bruto_precatorio: Decimal
    ir_calculado: Decimal
    base_calculo_liquida: Decimal
    valor_liquido_cedivel: Decimal

def calcular(params: CalcParams) -> CalcResult:
    # Entradas base
    principal = D(params.principal)
    valor_face = D(params.valor_precatorio)
    pago_super = D(params.pago_superpreferencia)

    # 1) Antes da formação: IPCA-E + 6% a.a. (≈ 0,5% a.m.)
    r_mensal_antes = annual_to_monthly_rate(params.juros_aa_antes_formacao)
    fator_antes = compose_factors(params.ipca_antes_formacao or [], r_mensal_antes)

    principal_apos_antes = quantize_cents(principal * fator_antes)
    juros_antes = quantize_cents(principal_apos_antes - principal)  # diferença é “juros + correção” práticos

    # 2) Período de graça: apenas IPCA-E (0% a.a.)
    fator_grace = compose_factors(params.ipca_grace or [], D(0))
    principal_apos_grace = quantize_cents(principal_apos_antes * fator_grace)
    correcoes_grace = principal_apos_grace - principal_apos_antes  # apenas correção, sem juros adicionais

    # 3) Após graça: IPCA-E + 2% a.a.
    r_mensal_pos = annual_to_monthly_rate(params.juros_aa_pos_grace)
    fator_pos = compose_factors(params.ipca_pos_grace or [], r_mensal_pos)
    principal_final = quantize_cents(principal_apos_grace * fator_pos)

    # Juros posteriores (aproxima: diferença menos apenas correções)
    # Para isolar “juros de mora posteriores”, calculamos qual seria o valor só com IPCA:
    fator_somente_ipca_pos = compose_factors(params.ipca_pos_grace or [], D(0))
    apenas_ipca_pos_val = quantize_cents(principal_apos_grace * fator_somente_ipca_pos)
    juros_posteriores = quantize_cents(principal_final - apenas_ipca_pos_val)

    # Valor bruto (sem abater superpreferência ainda), conforme quadro
    valor_bruto_precatorio = principal_final

    # IR (se incide, sobre juros de mora totais = “juros_antes só da parte juros” + “juros_posteriores”)
    # Aproximação: tratamos "juros de mora anteriores" como o excedente sobre a correção monetária.
    # Sem decompor o IPCA vs. juros mês a mês, adotamos a regra prática: IR apenas sobre ‘juros_posteriores’.
    ir_calculado = D(0)
    if params.incide_ir and params.ir_rate > 0:
        ir_calculado = quantize_cents(juros_posteriores * D(params.ir_rate))

    # Abate superpreferência após atualização total
    base_calculo_liquida = quantize_cents(valor_bruto_precatorio - ir_calculado)
    valor_liquido_cedivel = quantize_cents(base_calculo_liquida - pago_super)

    return CalcResult(
        principal_atualizado=principal_final,
        juros_mora_antes=juros_antes,               # agregado (antes da formação)
        juros_mora_posteriores=juros_posteriores,   # após graça
        valor_bruto_precatorio=valor_bruto_precatorio,
        ir_calculado=ir_calculado,
        base_calculo_liquida=base_calculo_liquida,
        valor_liquido_cedivel=valor_liquido_cedivel,
    )

# ---------- exemplo de uso ----------

if __name__ == "__main__":
    # EXEMPLO: gere 12 meses antes, 12 meses de graça, 5 meses após
    # Use aqui suas séries reais do IPCA-E por mês (frações, e.g., 0.0032 = 0,32%).
    ipca_antes = [D("0.0032")] * 12       # 12 meses, 0,32%/mês
    ipca_grace = [D("0.0028")] * 12       # 12 meses, 0,28%/mês
    ipca_pos   = [D("0.0030")] * 5        # 5 meses, 0,30%/mês

    params = CalcParams(
        valor_precatorio=D("100000.00"),
        principal=D("100000.00"),
        honorarios_percent=D("0.00"),
        pago_superpreferencia=D("0.00"),
        incide_ir=True,
        ir_rate=D("0.15"),  # 15% sobre juros posteriores (ajuste conforme sua regra)
        dt_formacao=date(2024, 1, 10),
        dt_vencimento=date(2025, 1, 10),
        dt_pagamento=date(2025, 6, 10),
        ipca_antes_formacao=ipca_antes,
        ipca_grace=ipca_grace,
        ipca_pos_grace=ipca_pos,
    )

    res = calcular(params)

    print("=== Resultado ===")
    print(f"Principal atualizado:      R$ {res.principal_atualizado:,.2f}")
    print(f"Juros de mora (anteriores): R$ {res.juros_mora_antes:,.2f}")
    print(f"Juros de mora (posteriores):R$ {res.juros_mora_posteriores:,.2f}")
    print(f"Valor bruto Precatório:     R$ {res.valor_bruto_precatorio:,.2f}")
    print(f"IR calculado:               R$ {res.ir_calculado:,.2f}")
    print(f"Base de Cálculo Líquida:    R$ {res.base_calculo_liquida:,.2f}")
    print(f"Valor Líquido Cedível:      R$ {res.valor_liquido_cedivel:,.2f}")
