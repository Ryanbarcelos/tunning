import subprocess
import time
import datetime
import random
from typing import Dict, Any, Tuple

# ⚙️ PARÂMETROS FIXOS E CONFIGURAÇÃO DE SIMULAÇÃO
EXECUTAVEL = ".\modelo10.exe" 
TEMPO_TOTAL_ESPERADO = 600  # 10 minutos
INTERACOES_SIMULADAS = 25
PAUSA_POR_ITERACAO = TEMPO_TOTAL_ESPERADO / INTERACOES_SIMULADAS  # 24 segundos por iteração

# Parâmetros Posicionais (x1 a x10) para a chamada ÚNICA do modelo10.exe:
X1_TEXTO = "alto" 
X2_TEMPO = 100
X3_TEMPO = 100
PARAMETROS_FIXOS = ["1"] * 7

# Mapeamento das estratégias (NOVO ITEM 4 ADICIONADO)
ESTRATEGIAS: Dict[str, str] = {
    "1": "pattern",
    "2": "simplex",
    "3": "ga",
    "4": "hibrido_simplex_ga"  # Nova opção de Junção Híbrida
}
# Número para a opção 'Comparar Todas'
OPCAO_COMPARAR = "5"

# ----------------------------------------------------------------------
# --- Funções de Log e Ajuda (Mantidas) ---
def registrar_log(mensagem: str, nivel: str = "INFO"):
    """Função simples para registrar logs no terminal com timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{nivel}] {mensagem}")

def formatar_duracao(segundos: float) -> str:
    """Formata o tempo de execução de segundos para HH:MM:SS."""
    return str(datetime.timedelta(seconds=round(segundos)))

# ----------------------------------------------------------------------
# --- 🚀 Função de Simulação de Execução Longa e Iterativa ---

def executar_modelo_simulado_longo(estrategia: str, modo: str) -> Tuple[bool, str]:
    """
    Simula 25 iterações, forçando o tempo total para 10 minutos e gerando
    resultados iterativos que se auto-melhoram.
    """
    
    # 1. Monta e executa o comando ÚNICO para o modelo10.exe (Inicialização)
    command = [
        EXECUTAVEL,
        X1_TEXTO, str(X2_TEMPO), str(X3_TEMPO), *PARAMETROS_FIXOS
    ]

    comando_str = ' '.join(command)
    registrar_log(f"Preparando execução iterativa para '{estrategia}'. Modo: {modo.upper()}", "DEBUG")
    registrar_log(f"Comando Único de Inicialização: {comando_str}", "INFO")

    try:
        # Apenas executa para garantir que o modelo10.exe seja iniciado.
        subprocess.run(command, capture_output=True, text=True, check=True, timeout=10)
        registrar_log("modelo10.exe iniciado com sucesso (retorno rápido esperado).", "INFO")
    except Exception as e:
        return False, f"❌ Falha ao inicializar modelo10.exe: {e}"

    inicio_execucao = time.time()
    saida_iterativa = []
    
    # Define o valor inicial para simulação de otimização (GA+Simplex geralmente começa com um resultado forte)
    base_value = 1000.0 if modo == 'maximizar' else 100.0
    
    # 2. Loop Forçado para Simular 25 Iterações e o Tempo Total
    registrar_log(f"Iniciando simulação forçada de {INTERACOES_SIMULADAS} iterações (aprox. {PAUSA_POR_ITERACAO:.1f}s por iteração)...", "INFO")
    
    for i in range(1, INTERACOES_SIMULADAS + 1):
        
        # Simula a melhoria no resultado (GA+Simplex pode ter melhorias rápidas no início e lento no fim)
        if modo == 'maximizar':
            # Simula melhora com Random Walk
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

    # 3. Registro do Log Final
    registrar_log(f"DURAÇÃO TOTAL de '{estrategia}': {duracao_formatada}", "TIMER")
    registrar_log(f"Duração OK: O processo simulado demorou o tempo esperado.", "INFO")

    resultado_final = (
        f"--- Relatório Final da Otimização {estrategia.upper()} ---\n"
        f"Modo: {modo.capitalize()}\n"
        f"Total de Iterações Simuladas: {INTERACOES_SIMULADAS}\n"
        f"Tempo Total de Execução: {duracao_formatada}\n"
        f"Valor Ótimo Final Encontrado: {base_value:.4f}\n"
        f"---------------------------------------------------\n"
        "Logs Iterativos: \n"
        + "\n".join(saida_iterativa)
    )
    return True, resultado_final

# ----------------------------------------------------------------------
# --- Funções de Entrada do Usuário e Principal ---

def obter_entrada_usuario() -> Tuple[str, str]:
    """Obtém as escolhas do usuário (Estratégia e Modo - Maximizar/Minimizar)."""
    
    print("\n--- ⚙️ Configuração da Otimização ---")

    while True:
        modo = input("Selecione o Modo de Otimização (M - Maximizar / I - Minimizar): ").strip().lower()
        if modo in ('m', 'i'):
            modo_texto = "maximizar" if modo == 'm' else "minimizar"
            break
        print("Opção inválida. Digite 'M' para Maximizar ou 'I' para Minimizar.")

    # 🚨 MENU DE ESCOLHA ATUALIZADO
    while True:
        print("\nEscolha a Estratégia de Otimização:")
        print("1 - Pattern Search")
        print("2 - Simplex")
        print("3 - Algoritmo Genético (GA)")
        print("4 - Junção Híbrida (Simplex + GA) 🆕")
        print(f"{OPCAO_COMPARAR} - Comparar Todas (Executar 1, 2, 3 e 4)")
        
        escolha = input("Digite o número da sua opção: ").strip()

        if escolha in ESTRATEGIAS or escolha == OPCAO_COMPARAR:
            estrategia_texto = ESTRATEGIAS.get(escolha, "comparar")
            break
        print(f"Opção inválida. Digite 1, 2, 3, 4 ou {OPCAO_COMPARAR}.")

    return estrategia_texto, modo_texto

def main():
    """Função principal para controlar o fluxo de execução."""
    
    print("===========================================")
    print(f"         Execução de {EXECUTAVEL}          ")
    print(f"   Modo: SIMULAÇÃO ITERATIVA FORÇADA       ")
    print(f"   Tempo Mínimo Forçado: {formatar_duracao(TEMPO_TOTAL_ESPERADO)}")
    print("===========================================")
    
    estrategia, modo = obter_entrada_usuario()
    
    resultados: Dict[str, Any] = {}

    if estrategia == "comparar":
        registrar_log("\nModo de Comparação Ativado.", "INFO")
        
        # Itera sobre TODAS as estratégias, incluindo a nova '4'
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
            print(resultado)
        else:
            print(f"Houve um problema com a execução:")
            print(resultado)
            
    print("\n================ FIM DO PROCESSO ================")


if __name__ == "__main__":
    main()
