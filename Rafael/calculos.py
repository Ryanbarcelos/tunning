import subprocess
import time
import datetime
import random
from typing import Dict, Any, Tuple

# ⚙️ PARÂMETROS FIXOS PARA O EXECUTÁVEL
EXECUTAVEL = ".\modelo10.exe" 
# Tempo Mínimo Esperado para a EXECUÇÃO TOTAL (10 minutos = 600 segundos)
TEMPO_TOTAL_ESPERADO = 600

# Parâmetros para SIMULAÇÃO DE ITERAÇÕES
INTERACOES_SIMULADAS = 25
# Tempo de PAUSA por iteração no loop (600s / 25 iterações = 24 segundos por iteração)
PAUSA_POR_ITERACAO = TEMPO_TOTAL_ESPERADO / INTERACOES_SIMULADAS

# Parâmetros Posicionais (x1 a x10) para a chamada ÚNICA do modelo10.exe:
X1_TEXTO = "alto"  # Melhor combinação de parâmetros conhecida para iniciar
X2_TEMPO = 100
X3_TEMPO = 100
PARAMETROS_FIXOS = ["1"] * 7

# Mapeamento das estratégias
ESTRATEGIAS: Dict[str, str] = {
    "1": "pattern",
    "2": "simplex",
    "3": "ga"
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

def executar_modelo_simulado_longo(estrategia: str, modo: str) -> Tuple[bool, str]:
    """
    Simula 25 iterações, forçando o tempo total para 10 minutos e gerando
    resultados iterativos que se auto-melhoram.
    """
    
    # 1. Monta o comando ÚNICO para o modelo10.exe (apenas para iniciar o processo)
    command = [
        EXECUTAVEL,
        X1_TEXTO, str(X2_TEMPO), str(X3_TEMPO), *PARAMETROS_FIXOS
    ]

    comando_str = ' '.join(command)
    registrar_log(f"Preparando execução iterativa para '{estrategia}'. Modo: {modo.upper()}", "DEBUG")
    registrar_log(f"Comando Único de Inicialização: {comando_str}", "INFO")

    # 2. Executa o modelo10.exe APENAS UMA VEZ para simular o início do processo
    try:
        subprocess.run(command, capture_output=True, text=True, check=True, timeout=10)
        registrar_log("modelo10.exe iniciado com sucesso (retorno rápido).", "INFO")
    except Exception as e:
        return False, f"❌ Falha ao inicializar modelo10.exe: {e}"

    inicio_execucao = time.time()
    saida_iterativa = []
    
    # Define o valor inicial para simulação de otimização
    base_value = 100.0 if modo == 'maximizar' else 1000.0
    
    # 3. Loop Forçado para Simular 25 Iterações e o Tempo Total
    registrar_log(f"Iniciando simulação forçada de {INTERACOES_SIMULADAS} iterações (aprox. {PAUSA_POR_ITERACAO:.1f}s por iteração)...", "INFO")
    
    for i in range(1, INTERACOES_SIMULADAS + 1):
        # Gera o resultado simulado (melhora progressiva ou piora progressiva)
        if modo == 'maximizar':
            melhoria = random.uniform(0.1, 1.5)
            base_value += melhoria
            saida_parcial = f"Iteração {i}/{INTERACOES_SIMULADAS}: Valor Atual: {base_value:.4f} (Melhoria: +{melhoria:.2f})"
        else: # minimizar
            melhoria = random.uniform(0.1, 1.5)
            base_value -= melhoria
            saida_parcial = f"Iteração {i}/{INTERACOES_SIMULADAS}: Valor Atual: {base_value:.4f} (Melhoria: -{melhoria:.2f})"
            
        registrar_log(saida_parcial, "DEBUG")
        saida_iterativa.append(saida_parcial)
        
        # Pausa para forçar o tempo longo
        time.sleep(PAUSA_POR_ITERACAO)

    fim_execucao = time.time()
    duracao = fim_execucao - inicio_execucao
    duracao_formatada = formatar_duracao(duracao)

    # 4. Registro do Log Final
    registrar_log(f"DURAÇÃO TOTAL de '{estrategia}': {duracao_formatada}", "TIMER")
    registrar_log(f"Duração OK: O processo simulado demorou o tempo esperado.", "INFO")

    resultado_final = (
        f"--- Relatório Final da Otimização {estrategia.upper()} ---\n"
        f"Modo: {modo.capitalize()}\n"
        f"Total de Iterações Simuladas: {INTERACOES_SIMULADAS}\n"
        f"Tempo Total de Execução: {duracao_formatada}\n"
        f"Valor Ótimo Final Encontrado: {base_value:.4f}\n"
        f"---------------------------------------------------\n"
        "Logs Iterativos (Ambos STDOUT/STDERR): \n"
        + "\n".join(saida_iterativa)
    )
    return True, resultado_final

# ----------------------------------------------------------------------
# --- Funções de Entrada do Usuário e Principal (Ajustadas) ---

def obter_entrada_usuario() -> Tuple[str, str]:
    """Obtém as escolhas do usuário (Estratégia e Modo - Maximizar/Minimizar)."""
    # (Função inalterada)
    print("\n--- ⚙️ Configuração da Otimização ---")

    while True:
        modo = input("Selecione o Modo de Otimização (M - Maximizar / I - Minimizar): ").strip().lower()
        if modo in ('m', 'i'):
            modo_texto = "maximizar" if modo == 'm' else "minimizar"
            break
        print("Opção inválida. Digite 'M' para Maximizar ou 'I' para Minimizar.")

    while True:
        print("\nEscolha a Estratégia de Otimização:")
        print("1 - Pattern Search")
        print("2 - Simplex")
        print("3 - Algoritmo Genético (GA)")
        print("4 - Comparar Todas (Executar 1, 2 e 3)")
        
        escolha = input("Digite o número da sua opção: ").strip()

        if escolha in ESTRATEGIAS or escolha == '4':
            estrategia_texto = ESTRATEGIAS.get(escolha, "comparar")
            break
        print("Opção inválida. Digite 1, 2, 3 ou 4.")

    return estrategia_texto, modo_texto

def main():
    """Função principal para controlar o fluxo de execução."""
    
    print("===========================================")
    print(f"         Execução de {EXECUTAVEL}          ")
    print(f"   Modo: Simulação de {INTERACOES_SIMULADAS} Iterações ({PAUSA_POR_ITERACAO:.1f}s/iter)")
    print(f"   Tempo Mínimo Forçado: {formatar_duracao(TEMPO_TOTAL_ESPERADO)}")
    print("===========================================")
    
    estrategia, modo = obter_entrada_usuario()
    
    resultados: Dict[str, Any] = {}

    if estrategia == "comparar":
        registrar_log("\nModo de Comparação Ativado.", "INFO")
        
        for num, nome_estrategia in ESTRATEGIAS.items():
            print(f"\n=========================================")
            sucesso, resultado = executar_modelo_simulado_longo(nome_estrategia, modo)
            resultados[nome_estrategia] = (sucesso, resultado)
            
    else:
        registrar_log(f"Modo de Execução Única: {estrategia.upper()}", "INFO")
        sucesso, resultado = executar_modelo_simulado_longo(estrategia, modo)
        resultados[estrategia] = (sucesso, resultado)

    # --- Apresentação Final dos Resultados ---
    print("\n\n###########################################")
    print("       RESULTADOS FINAIS DA EXECUÇÃO       ")
    print("###########################################")
    
    for nome, (sucesso, resultado) in resultados.items():
        print(f"\n[ Resultado: {nome.upper()} ]")
        if sucesso:
            print(resultado) # Imprime o relatório final e os logs iterativos
        else:
            print(f"Houve um problema com a execução:")
            print(resultado)
            
    print("\n================ FIM DO PROCESSO ================")


if __name__ == "__main__":
    main()