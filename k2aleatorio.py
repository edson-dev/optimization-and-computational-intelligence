
from pgmpy.readwrite import XMLBIFWriter
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import K2Score, BayesianEstimator
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import random
import time

from sql import RepositorySQL


def k2(filename, dataset, parents_nmax, num_iterations=10):
    variables = list(dataset.columns)
    with open(f'result/{filename}_random.txt', 'w') as file:  # Abra um arquivo de texto para escrita
        file.write(f'Ordem das variáveis iniciais: {variables}\n')

        estimator = K2Score(dataset)
        models_and_scores = []
        best_model = None
        best_score = float('-inf')
        best_order = None
        worst_model = None
        worst_score = float('inf')
        worst_order = None
        total_score = 0

        for iteration in range(num_iterations):
            random_order = random.sample(variables, len(variables))
            print(type(random_order))
            file.write(f'\nOrdem das variáveis aleatórias (iteração {iteration + 1}): {random_order}\n')
            print(f'Ordem das variáveis aleatórias (iteração {iteration + 1}): {random_order}')
            model = BayesianNetwork()
            model.add_nodes_from(random_order)

            for i in range(1, len(random_order)):
                node = random_order[i]  # no atual
                previous_nodes = random_order[:i]  # nos anteriores ao no atual
                parents = []  # pais do no atual
                P_old = estimator.local_score(node, parents)
                proceed = True

                while proceed and (len(parents) < parents_nmax):
                    candidates = list(set(previous_nodes) - set(parents))  # nos candidatos para pais do no atual
                    P_new = P_old  # new probability

                    for candidate in candidates:
                        candidate_score = estimator.local_score(node, parents + [candidate])  # pontuacao dos nos pais

                        if candidate_score > P_new:
                            candidates_best = candidate  # melhor candidato para no pai
                            P_new = candidate_score

                    if P_new > P_old:
                        P_old = P_new
                        parents.append(candidates_best)
                        model.add_edge(candidates_best, node)

                    else:
                        proceed = False

            score = estimator.score(model)
            total_score += score

            if score > best_score:
                best_model = model
                best_score = score
                best_order = random_order

            if score < worst_score:
                worst_model = model
                worst_score = score
                worst_order = random_order

            models_and_scores.append((model, score))
            file.write(f"Iteração {iteration + 1} - Score: {score}\n")
            print(f"Iteração {iteration + 1} - Score: {score}")
            file.write(f'Estrutura: {model.edges}\n')
            print(f'Estrutura: {model.edges}')
            file.write(
                '------------------------------------------------------------------------------------------------')
            print('------------------------------------------------------------------------------------------------')

            # Calculate CPDs for the current model
            cpds = tabular_cpd(model, dataset)
            for node, cpd in zip(model.nodes, cpds):
                model.add_cpds(cpd)

        avg_score = total_score / num_iterations

        file.write("\nMelhor Ordem, Estrutura e Score:\n")
        file.write(f"Ordem: {best_order}\n")
        file.write(f"Estrutura: {best_model.edges}\n")
        file.write(f"Score: {best_score}\n")
        file.write(f"Média dos Scores: {avg_score}\n")
        print("\nMelhor Ordem, Estrutura e Score:")
        print(f"Ordem: {best_order}")
        print(f"Estrutura: {best_model.edges}")
        print(f"Score: {best_score}")
        print(f"Média dos Scores: {avg_score}")

        file.write("\nPior Ordem, Estrutura e Score:\n")
        file.write(f"Ordem: {worst_order}\n")
        file.write(f"Estrutura: {worst_model.edges}\n")
        file.write(f"Score: {worst_score}\n")
        print("\nPior Ordem, Estrutura e Score:")
        print(f"Ordem: {worst_order}")
        print(f"Estrutura: {worst_model.edges}")
        print(f"Score: {worst_score}")

        return models_and_scores, best_model, worst_model, best_score


# Função para encontrar as CPDs
def tabular_cpd(model, data):
    for column in data.columns:
        data[column] = pd.Categorical(data[column])
    estimator = BayesianEstimator(model, data)
    cpds = [estimator.estimate_cpd(node) for node in model.nodes]
    return cpds


if __name__ == "__main__":
    file_name = "asia"  # "hepartwo",contact-lenses
    data = pd.read_csv(f'data/{file_name}.csv')
    best_model = k2(file_name,data, 4)
    cpds = tabular_cpd(best_model[1], data)

    print(f'Modelo: {best_model}')

    #P2

    # Carregar os dados do CSV
    data = pd.read_csv(f'data/{file_name}.csv')  # caminho para o arquivo CSV
    # Mapear os valores nominais para números inteiros únicos
    data = data.apply(LabelEncoder().fit_transform)
    variables = list(data.columns)

    print("DataFrame original:")
    print(list(data))
    num_iterations = 10

    start_time = time.time()
    models_and_scores, best_model, worst_model, best_score = k2(file_name,data, 4, num_iterations)
    cpds_best = tabular_cpd(best_model, data)
    cpds_worst = tabular_cpd(worst_model, data)
    end_time = time.time()

    # Adicione as CPDs ao melhor modelo
    for node, cpd in zip(best_model.nodes, cpds_best):
        best_model.add_cpds(cpd)

    for node, cpd in zip(worst_model.nodes, cpds_worst):
        worst_model.add_cpds(cpd)

    # Salve o modelo em formato XMLBIF
    bif_writer = XMLBIFWriter(best_model)
    bif_writer.write_xmlbif(f'result/{file_name}_random_best.xmlbif')

    bif_writer = XMLBIFWriter(worst_model)
    bif_writer.write_xmlbif(f'result/{file_name}_random_worst.xmlbif')

    # Calcule o tempo decorrido
    elapsed_time = end_time - start_time
    execution_time = elapsed_time

    with open(f'result/{file_name}_random.txt', 'a') as file:  # Abrir o arquivo para atualizar
        file.write(f'Tempo: {execution_time}\n')

    with RepositorySQL("sqlite:///./masters.db") as repo:
        a = repo.upsert("optimization", {"algorithm": "ramdom","base": file_name,"feature": list(best_model.edges)[0][0], "order": str(list(best_model)), "structure": str(best_model.edges), "score": best_score, "time": execution_time, "xmlbit": f'result/{file_name}_random_best.xmlbif'},keys=["algorithm","base"])
