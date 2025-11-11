#!/usr/bin/env python3
"""
tuning.py
Suporta: pattern search, genetic algorithm (GA), particle swarm optimization (PSO)
Critério: minimizar tempo de execução do executável definido em config.json
"""

import json
import subprocess
import time
import random
import argparse
import math
from copy import deepcopy

# ----------------------------
# UTILS: carregar config
# ----------------------------
def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    executable = cfg.get("executable") or cfg.get("exe") or cfg.get("program")
    params_raw = cfg.get("parameters")

    params = []  # lista com dicts: {name,type, values OR min,max,step}
    if isinstance(params_raw, list):
        for p in params_raw:
            # espera que p contenha 'name' e 'type'
            params.append(p)
    elif isinstance(params_raw, dict):
        # formato gerado pelo configurador (nome -> {min,max,step})
        for name, info in params_raw.items():
            # detectar se é categorico: se tiver key 'values'
            if "values" in info:
                params.append({
                    "name": name,
                    "type": "categorical",
                    "values": info["values"]
                })
            else:
                params.append({
                    "name": name,
                    "type": "int",
                    "min": int(info["min"]),
                    "max": int(info["max"]),
                    "step": int(info.get("step", 1))
                })
    else:
        raise ValueError("Formato de 'parameters' em config.json não reconhecido")

    return executable, params

# ----------------------------
# REPRESENTAÇÃO E CONVERSÕES
# ----------------------------
def random_value_for_param(p):
    if p["type"] == "categorical":
        return random.choice(p["values"])
    elif p["type"] == "int":
        return random.randint(p["min"], p["max"])
    else:
        raise ValueError("Tipo de parâmetro desconhecido")

def decode_candidate(params, candidate):
    """
    candidate: lista de values (ints or categorical values or float indices for PSO)
    Retorna lista de strings prontos para passar ao executável.
    """
    args = []
    for p, v in zip(params, candidate):
        if p["type"] == "categorical":
            # se v for número (índice) converte, senão assume já é valor
            if isinstance(v, (int, float)):
                idx = int(round(v))
                idx = max(0, min(len(p["values"]) - 1, idx))
                args.append(str(p["values"][idx]))
            else:
                args.append(str(v))
        elif p["type"] == "int":
            # aceitar float por segurança (PSO)
            val = int(round(v))
            val = max(p["min"], min(p["max"], val))
            args.append(str(val))
        else:
            raise ValueError("Tipo desconhecido")
    return args

# ----------------------------
# AVALIACAO: roda executável e mede tempo
# ----------------------------
def avaliar_exec(executable, args_list, timeout=None):
    """
    Roda: [executable] + args_list
    Retorna: tempo_em_segundos (float)
    Suprime stdout/stderr para não poluir o console.
    """
    cmd = [executable] + args_list
    inicio = time.time()
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
    except subprocess.TimeoutExpired:
        # penalidade alta se exceder timeout (tratamos como muito ruim)
        return float("inf")
    fim = time.time()
    return fim - inicio

# ----------------------------
# PATTERN SEARCH (já conhecido)
# ----------------------------
def pattern_search(executable, params, initial=None, step_initial=10):
    # construir vetor inicial
    if initial is None:
        candidate = []
        for p in params:
            if p["type"] == "categorical":
                candidate.append(p["values"][0])
            else:
                candidate.append((p["min"] + p["max"]) // 2)
    else:
        candidate = initial[:]

    # se param int tiver step definido, usaremos; senão default step_initial
    step = step_initial
    # para int, torque scale: garantir que step útil não exceda range
    melhor = avaliar_exec(executable, decode_candidate(params, candidate))
    print(f"Iniciando busca... Tempo inicial: {melhor:.4f} s")

    while step >= 1:
        melhorou = False
        # testar variações categóricas (trocar por cada possivel valor)
        for i, p in enumerate(params):
            if p["type"] == "categorical":
                for val in p["values"]:
                    cand = candidate[:]
                    cand[i] = val
                    t = avaliar_exec(executable, decode_candidate(params, cand))
                    if t < melhor:
                        melhor, candidate = t, cand
                        melhorou = True
                        print(f"[X{i+1}] Novo melhor: {melhor:.4f}s com x{i+1} = {val}")
            else:
                # int: testar +step e -step
                for delta in (-step, step):
                    cand = candidate[:]
                    cand[i] = max(p["min"], min(p["max"], cand[i] + delta))
                    t = avaliar_exec(executable, decode_candidate(params, cand))
                    if t < melhor:
                        melhor, candidate = t, cand
                        melhorou = True
                        print(f"[X{i+1}] Novo melhor: {melhor:.4f}s com {decode_candidate(params, cand)}")
        if not melhorou:
            step = step // 2
            print(f"Reduzindo passo para {step}")

    return candidate, melhor

# ----------------------------
# GENETIC ALGORITHM (GA)
# ----------------------------
def ga_search(executable, params, pop_size=20, generations=30, crossover_rate=0.8, mutation_rate=0.2, tournament_k=3):
    # Inicializa população (lista de indivíduos: cada um uma lista de valores)
    def random_individual():
        ind = []
        for p in params:
            if p["type"] == "categorical":
                ind.append(random.choice(p["values"]))
            else:
                ind.append(random.randint(p["min"], p["max"]))
        return ind

    def fitness(ind):
        # fitness = tempo (quanto menor melhor)
        args = decode_candidate(params, ind)
        return avaliar_exec(executable, args)

    def tournament_selection(pop, scores):
        # retorna um individual
        best = None
        best_score = float("inf")
        for _ in range(tournament_k):
            i = random.randrange(len(pop))
            if scores[i] < best_score:
                best_score = scores[i]
                best = pop[i]
        return deepcopy(best)

    def crossover(a, b):
        # Uniform crossover por gene
        child1, child2 = deepcopy(a), deepcopy(b)
        for i, p in enumerate(params):
            if random.random() < 0.5:
                child1[i], child2[i] = child2[i], child1[i]
        return child1, child2

    def mutate(ind):
        for i, p in enumerate(params):
            if random.random() < mutation_rate:
                if p["type"] == "categorical":
                    ind[i] = random.choice(p["values"])
                else:
                    # mutação gaussiana discreta
                    span = max(1, (p["max"] - p["min"]) // 4)
                    ind[i] = int(round(ind[i] + random.randint(-span, span)))
                    ind[i] = max(p["min"], min(p["max"], ind[i]))

    # criar população
    population = [random_individual() for _ in range(pop_size)]
    scores = [fitness(ind) for ind in population]

    best_idx = min(range(len(scores)), key=lambda i: scores[i])
    best = deepcopy(population[best_idx])
    best_score = scores[best_idx]
    print(f"GA: geração 0, melhor tempo: {best_score:.4f}s")

    for gen in range(1, generations + 1):
        new_pop = []
        # elitism: manter o melhor
        new_pop.append(deepcopy(best))
        while len(new_pop) < pop_size:
            a = tournament_selection(population, scores)
            b = tournament_selection(population, scores)
            if random.random() < crossover_rate:
                c1, c2 = crossover(a, b)
            else:
                c1, c2 = a, b
            mutate(c1)
            mutate(c2)
            new_pop.append(c1)
            if len(new_pop) < pop_size:
                new_pop.append(c2)

        population = new_pop
        scores = [fitness(ind) for ind in population]

        idx = min(range(len(scores)), key=lambda i: scores[i])
        if scores[idx] < best_score:
            best_score = scores[idx]
            best = deepcopy(population[idx])
            print(f"GA: geração {gen}, novo melhor: {best_score:.4f}s -> {decode_candidate(params, best)}")
        else:
            if gen % 5 == 0:
                print(f"GA: geração {gen}, melhor até agora: {best_score:.4f}s")

    return best, best_score

# ----------------------------
# PARTICLE SWARM OPTIMIZATION (PSO)
# ----------------------------
def pso_search(executable, params, pop_size=30, iterations=50, w=0.6, c1=1.5, c2=1.5):
    # representaremos cada partícula como vetor de floats:
    # - para int: valor numérico (entre min e max)
    # - para categorical: índice (0 .. len(values)-1)
    dim = len(params)

    def rand_position():
        pos = []
        for p in params:
            if p["type"] == "categorical":
                pos.append(random.randint(0, len(p["values"]) - 1))
            else:
                pos.append(random.uniform(p["min"], p["max"]))
        return pos

    def clamp_position(pos):
        for i, p in enumerate(params):
            if p["type"] == "categorical":
                pos[i] = max(0, min(len(p["values"]) - 1, int(round(pos[i]))))
            else:
                pos[i] = max(p["min"], min(p["max"], pos[i]))
        return pos

    # inicialização
    particles = [rand_position() for _ in range(pop_size)]
    velocities = [[0.0] * dim for _ in range(pop_size)]
    pbest = deepcopy(particles)
    pbest_scores = [float("inf")] * pop_size
    gbest = None
    gbest_score = float("inf")

    # avaliar inicial
    for i, pos in enumerate(particles):
        args = decode_candidate(params, pos)
        sc = avaliar_exec(executable, args)
        pbest_scores[i] = sc
        if sc < gbest_score:
            gbest_score = sc
            gbest = deepcopy(pos)
    print(f"PSO: inicial melhor {gbest_score:.4f}s")

    for it in range(1, iterations + 1):
        for i in range(pop_size):
            # atualiza velocidade e posição
            for d in range(dim):
                r1, r2 = random.random(), random.random()
                # velocidade baseada em diferença entre melhores (personal/global)
                vel = (w * velocities[i][d]
                       + c1 * r1 * ((pbest[i][d]) - particles[i][d])
                       + c2 * r2 * ((gbest[d]) - particles[i][d]))
                velocities[i][d] = vel
                particles[i][d] = particles[i][d] + vel

            # clamp/round
            clamp_position(particles[i])

            # avaliar
            args = decode_candidate(params, particles[i])
            sc = avaliar_exec(executable, args)

            # atualizar pbest
            if sc < pbest_scores[i]:
                pbest_scores[i] = sc
                pbest[i] = deepcopy(particles[i])

                # atualizar gbest
                if sc < gbest_score:
                    gbest_score = sc
                    gbest = deepcopy(particles[i])
                    print(f"PSO: it {it}, novo global {gbest_score:.4f}s -> {decode_candidate(params, gbest)}")

        if it % 10 == 0:
            print(f"PSO: it {it}, melhor até agora: {gbest_score:.4f}s")

    return gbest, gbest_score

# ----------------------------
# CLI e execução
# ----------------------------
def main():
    parser = argparse.ArgumentParser(description="Auto-tuning: pattern/ga/pso (minimiza tempo de execução)")
    parser.add_argument("--config", default="config.json", help="Arquivo de configuração JSON")
    parser.add_argument("--method", choices=["pattern", "ga", "pso"], default="pattern")
    # GA params
    parser.add_argument("--pop", type=int, default=20, help="Tamanho da população (GA/PSO)")
    parser.add_argument("--gens", type=int, default=30, help="Gerações (GA)")
    # PSO params
    parser.add_argument("--iters", type=int, default=50, help="Iterações (PSO)")
    parser.add_argument("--seed", type=int, default=None, help="Seed aleatório")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    executable, params = load_config(args.config)
    if executable is None:
        raise ValueError("Executável não encontrado no config.json")

    print(f"Executável: {executable}")
    print("Parâmetros:")
    for p in params:
        print(" ", p)

    if args.method == "pattern":
        cand, score = pattern_search(executable, params)
    elif args.method == "ga":
        cand, score = ga_search(executable, params, pop_size=args.pop, generations=args.gens)
    elif args.method == "pso":
        cand, score = pso_search(executable, params, pop_size=args.pop, iterations=args.iters)
    else:
        raise ValueError("Método desconhecido")

    print("\n====== RESULTADO FINAL ======")
    print("Melhor configuração:")
    for name, val in zip([p.get("name", f"x{i+1}") for i, p in enumerate(params)], cand):
        print(f"  {name}: {val}")
    print(f"Menor tempo de execução encontrado: {score:.4f} segundos")

if __name__ == "__main__":
    main()
