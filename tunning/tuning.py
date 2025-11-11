import subprocess
import time

# Caminho do executável do modelo
PATH_EXE = r"C:\Users\aluno\Downloads\modelo10.exe"

def avaliar_modelo(x1, x):
    """
    Roda o modelo com os parâmetros e mede o tempo de execução.
    Retorna o tempo (quanto menor, melhor).
    """
    cmd = [PATH_EXE, x1] + list(map(str, x))

    inicio = time.time()
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    fim = time.time()

    return fim - inicio


def pattern_search(x1_inicial, x_inicial):
    """
    Implementação do Pattern Search para minimização do tempo.
    """
    x1_opcoes = ["baixo", "medio", "alto"]
    x1 = x1_inicial
    x = x_inicial[:]

    passo = 10  # passo inicial de busca
    melhor = avaliar_modelo(x1, x)

    print(f"Iniciando busca... Tempo inicial: {melhor:.4f} s")

    while passo >= 1:
        melhorou = False

        # Testa variações do parâmetro textual x1
        for opc in x1_opcoes:
            valor = avaliar_modelo(opc, x)
            if valor < melhor:
                melhor = valor
                x1 = opc
                melhorou = True
                print(f"[X1] Novo melhor: {melhor:.4f}s com x1 = {x1}")

        # Testa variações dos inteiros x2..x10
        for i in range(len(x)):
            for delta in (-passo, passo):
                candidato = x[:]
                candidato[i] = max(1, min(100, candidato[i] + delta))
                valor = avaliar_modelo(x1, candidato)

                if valor < melhor:
                    melhor = valor
                    x = candidato
                    melhorou = True
                    print(f"[X{i+2}] Novo melhor: {melhor:.4f}s com {x}")

        # Se não melhorou, diminuímos o passo
        if not melhorou:
            passo //= 2
            print(f"Reduzindo passo para {passo}")

    return x1, x, melhor


if __name__ == "__main__":
    # Chute inicial
    x1_inicial = "medio"
    x_inicial = [50, 50, 50, 50, 50, 50, 50, 50, 50]

    melhor_x1, melhores_x, melhor_valor = pattern_search(x1_inicial, x_inicial)

    print("\n====== RESULTADO FINAL ======")
    print("Melhor valor para x1:", melhor_x1)
    print("Melhores valores para x2..x10:", melhores_x)
    print(f"Menor tempo de execução encontrado: {melhor_valor:.4f} segundos")
