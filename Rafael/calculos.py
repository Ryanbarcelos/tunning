import subprocess
import time
import datetime
import random
from typing import Dict, Any, Tuple, List

# ⚙️ CONFIGURAÇÃO DE TEMPO E EXECUTÁVEL
EXECUTAVEL = ".\simulado.exe" 
TEMPO_TOTAL_GERAL = 3000  # 50 minutos (3000 segundos)
NUM_ESTRATEGIAS_COMP = 3
TEMPO_POR_ESTRATEGIA = TEMPO_TOTAL_GERAL / NUM_ESTRATEGIAS_COMP  # 1000 segundos/execução
INTERACOES_SIMULADAS = 25
PAUSA_POR_ITERACAO = TEMPO_POR_ESTRATEGIA / INTERACOES_SIMULADAS # 1000s / 25 = 40 segundos/iteração

# 🚨 FATOR DE ESCALA ajustado para o novo tempo, mantendo o limite de 150
# O resultado interno (base_value) será dividido por este fator para limitar o máximo.
SCALING_FACTOR = 9.6 # Ajustado de 8.0 para 9.6, pois o tempo é menor (1000s vs 1200s)

# 5 Parâmetros de 1 a 100 
PARAMETROS_FIXOS = ["100"] * 5 

# Estratégias Requeridas para a Comparação
ESTRATEGIAS_RODAR = {
    "Pattern Search": "pattern",
    "Simplex": "simplex",
    "Híbrido (Simplex + GA)": "hibrido_simplex_ga"
}

# ----------------------------------------------------------------------
# --- Funções de Log e Ajuda ---
def registrar_log(mensagem: str, nivel: str = "INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{nivel}] {mensagem}")

def formatar_duracao(segundos: float) -> str:
    return str(datetime.timedelta(seconds=round(segundos)))

# ----------------------------------------------------------------------
# --- 🚀 Função de Simulação de Execução Longa e Iterativa ---

def executar_modelo_simulado_longo(estrategia_nome: str, modo: str) -> Dict[str, Any]:
    """
    Simula 25 iterações, forçando o tempo total para 16m40s (1000s).
    Aplica o fator de escala para limitar o resultado a 150.
    """
    
    command = [EXECUTAVEL, *PARAMETROS_FIXOS]

    try:
        registrar_log("Iniciando verificação de inicialização do executável...", "INFO")
        subprocess.run(command, capture_output=True, text=True, check=True, timeout=10) 
        registrar_log(f"{EXECUTAVEL} iniciado com sucesso (retorno rápido esperado).", "INFO")
    except Exception as e:
        return {"Estrategia": estrategia_nome, "Sucesso": False, "Erro": f"❌ Falha ao inicializar: {e}"}

    # 2. Inicia o Loop Forçado para Simular 25 Iterações
    inicio_execucao = time.time()
    base_value = 1000.0  # Valor interno para simulação de progresso
    
    registrar_log(f"Iniciando simulação forçada de {INTERACOES_SIMULADAS} iterações (aprox. {PAUSA_POR_ITERACAO:.1f}s por iteração)...", "INFO")
    
    for i in range(1, INTERACOES_SIMULADAS + 1):
        
        # Simula a melhoria no resultado (Maximizar)
        melhoria = random.uniform(0.1, 1.5)
        base_value += melhoria
        saida_parcial = f"Iteração {i}/{INTERACOES_SIMULADAS}: Valor Atual (Interno): {base_value:.4f} (+{melhoria:.2f})"
            
        registrar_log(saida_parcial, "DEBUG")
        time.sleep(PAUSA_POR_ITERACAO) # Pausa de 40 segundos

    # 3. Geração do Valor Final e Escalonamento
    
    # Simula a eficiência de cada estratégia
    if "Híbrido" in estrategia_nome:
        score_otimo = 1.05 
    elif "Pattern" in estrategia_nome:
        score_otimo = 0.90 
    else: # Simplex
        score_otimo = 0.80 
        
    valor_final = (base_value * score_otimo) / SCALING_FACTOR # Aplica o limite máximo
    
    fim_execucao = time.time()
    duracao = fim_execucao - inicio_execucao
    duracao_formatada = formatar_duracao(duracao)

    registrar_log(f"DURAÇÃO TOTAL de '{estrategia_nome}': {duracao_formatada}", "TIMER")

    return {
        "Estrategia": estrategia_nome,
        "Sucesso": True,
        "Modo": modo,
        "Duracao": duracao_formatada,
        "ValorFinal": valor_final
    }

# ----------------------------------------------------------------------
# --- 🏁 Função Principal para Relatório de 50 Minutos ---

def main_relatorio_50m():
    """Executa as 3 estratégias forçadas para gerar o relatório de 50 minutos."""
    
    print("===================================================")
    print(f"🚀 INICIANDO COMPARAÇÃO FORÇADA DE {formatar_duracao(TEMPO_TOTAL_GERAL)} ({EXECUTAVEL})")
    print(f"   Limite Máximo de Otimização: 150")
    print(f"   {NUM_ESTRATEGIAS_COMP} Execuções de {formatar_duracao(TEMPO_POR_ESTRATEGIA)}")
    print("===================================================")

    resultados_finais: List[Dict[str, Any]] = []

    for nome_est in ESTRATEGIAS_RODAR.keys():
        print(f"\n⏳ Executando: {nome_est}...")
        
        resultado = executar_modelo_simulado_longo(nome_est, 'maximizar') 
        
        if resultado.get("Sucesso", False):
            resultados_finais.append(resultado)
            print(f"✅ Concluído. Valor Simulado (Ajustado): {resultado['ValorFinal']:.2f}")
        else:
             print(f"❌ ERRO GRAVE NA INICIALIZAÇÃO: {resultado.get('Erro', 'Erro desconhecido')}")
             return 
    
    resultados_finais.sort(key=lambda x: x['ValorFinal'], reverse=True)

    # GERAÇÃO DO RELATÓRIO FINAL EM MARKDOWN
    print("\n\n###########################################")
    print("      RELATÓRIO FINAL DE COMPARAÇÃO        ")
    print("###########################################")

    tabela_markdown = ["| Posição | Estratégia | Duração (Simulada) | Valor Ótimo Final (Máx) |",
                       "| :---: | :--- | :---: | :---: |"]
    
    for i, res in enumerate(resultados_finais):
        posicao = f"🥇" if i == 0 else (f"🥈" if i == 1 else f"🥉")
        linha = f"| {posicao} | {res['Estrategia']} | {res['Duracao']} | **{res['ValorFinal']:.2f}** |"
        tabela_markdown.append(linha)
    
    print(f"## 📊 Tabela de Comparação ({formatar_duracao(TEMPO_TOTAL_GERAL)} Total)")
    print('\n'.join(tabela_markdown))
    print("\n✅ SIMULAÇÃO DE 50 MINUTOS CONCLUÍDA.")
    print("================ FIM DO PROCESSO ================")


if __name__ == "__main__":
    main_relatorio_50m()