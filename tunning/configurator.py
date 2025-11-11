import json

print("\n=== CONFIGURADOR DE MODELOS ===\n")

# Pergunta o nome do executável
exe = input("Digite o nome do executável (ex: modelo10.exe): ").strip()

# Garantir que terminou com .exe
if not exe.endswith(".exe"):
    exe += ".exe"

params = {}

print("\nAgora vamos cadastrar os parâmetros:")
print("(Exemplo de entrada: min=10 max=80 passo=5)")
print("Digite 'fim' quando terminar.\n")

while True:
    nome = input("Nome do parâmetro (ou 'fim' p/ encerrar): ").strip()

    if nome.lower() == "fim":
        break

    min_val = input(f"Valor mínimo para {nome}: ")
    max_val = input(f"Valor máximo para {nome}: ")
    passo = input(f"Passo de variação para {nome}: ")

    try:
        min_val = int(min_val)
        max_val = int(max_val)
        passo = int(passo)
    except:
        print("⚠ ERRO: Valores devem ser números inteiros. Tente novamente.\n")
        continue

    params[nome] = {
        "min": min_val,
        "max": max_val,
        "step": passo
    }

# Criar arquivo config.json
config = {
    "executable": exe,
    "parameters": params
}

with open("config.json", "w") as f:
    json.dump(config, f, indent=4)

print("\n✅ Arquivo 'config.json' criado com sucesso!")
print("Agora você pode rodar:")
print("\n   python tuning.py\n")

