import pandas as pd
import numpy as np
from pandas import DataFrame
from sklearn.preprocessing import LabelEncoder
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import K2Score, BayesianEstimator
import time

from sql import RepositorySQL


def correlacao_pearson(data:DataFrame, target):
    # Calcula a correlação de Pearson entre a coluna alvo e todas as outras colunas
    correlacoes = data.corr(method='pearson')[target]

    # Ordena as colunas com base na correlação em ordem decrescente
    correlacoes_ordenadas = correlacoes.abs().sort_values(ascending=False)

    # Reordena o DataFrame de acordo com as correlações ordenadas
    colunas_ordenadas = correlacoes_ordenadas.index
    df_ordenado = data[colunas_ordenadas]

    return df_ordenado


def k2(dataset, parents_nmax):
    estimator = K2Score(dataset)
    model = BayesianNetwork()
    nodes = list(dataset.columns)
    model.add_nodes_from(nodes)

    for i in range(1, len(nodes)):
        node = nodes[i]
        previous_nodes = nodes[:i]
        parents = []
        P_old = estimator.local_score(node, parents)
        proceed = True

        while proceed and (len(parents) < parents_nmax):
            candidates = list(set(previous_nodes) - set(parents))
            P_new = P_old

            for candidate in candidates:
                candidate_score = estimator.local_score(node, parents + [candidate])

                if candidate_score > P_new:
                    candidates_best = candidate
                    P_new = candidate_score

            if P_new > P_old:
                P_old = P_new
                parents.append(candidates_best)
                model.add_edge(candidates_best, node)
            else:
                proceed = False

    estrutura = list(model.edges)
    score = estimator.score(model)
    return estrutura, model, score


def tabular_cpd(model, data):
    for column in data.columns:
        data[column] = pd.Categorical(data[column])
    estimator = BayesianEstimator(model, data)
    cpds = [estimator.estimate_cpd(node) for node in model.nodes]
    return cpds

if __name__ == "__main__":
    file_name = "asia"  # "hepartwo"


    # Variáveis para acompanhar a melhor estrutura, melhor ordem, melhor score e a target_column relacionada
    melhor_estrutura = None
    melhor_ordem = None
    melhor_score = float('-inf')
    melhor_target = None

    data = pd.read_csv(f'data/{file_name}.csv')  # Caminho do dataset
    # Mapear os valores nominais para números inteiros únicos
    data = data.apply(LabelEncoder().fit_transform)
    variables = list(data.columns)

    start_time = time.time()

    print("DataFrame original:")
    print(list(data))

    for target in variables:
        if target == 'target':
            continue
        # Ordena o DataFrame por correlação
        df_ordenado = correlacao_pearson(data, target)
        variable_target = list(df_ordenado)
        estrutura, model, score = k2(df_ordenado, 4)
        print(f'Ordem gerada com a feature ({target}): {variable_target}')
        print(f'Estrutura gerada: {estrutura}')
        print(f'Score obtido: {score}')

        # Verificar se esta estrutura é a melhor até agora
        if score > melhor_score:
            melhor_estrutura = estrutura
            melhor_ordem = list(df_ordenado)
            melhor_score = score
            melhor_target = target
            melhor_model = model

    # Tabular as CPDs para o melhor modelo gerado
    cpds = tabular_cpd(melhor_model, df_ordenado)

    end_time = time.time()
    execution_time = end_time - start_time
    # P2
    from pgmpy.readwrite import XMLBIFWriter

    # Especifique o caminho do arquivo onde deseja salvar o arquivo XMLBIF
    file_path = f"result/{file_name}_pearson.xmlbif"

    # Abre o arquivo em modo de escrita
    with open(f"result/{file_name}_pearson.txt", "w") as arquivo:
        # Escreve os prints no arquivo
        arquivo.write(f'Melhor ordem gerada com a feature ({melhor_target}): {melhor_ordem}\n')
        arquivo.write(f'Estrutura dessa ordem: {melhor_estrutura}\n')
        arquivo.write(f'Score obtido dessa ordem: {melhor_score}\n')
        arquivo.write(f'Tempo: {execution_time}\n')

    with RepositorySQL("sqlite:///./masters.db") as repo:
        a = repo.upsert("optimization", {"algorithm": "pearson","base": file_name,"feature": melhor_target, "order": str(melhor_ordem), "structure": str(melhor_estrutura), "score": melhor_score, "time": execution_time, "xmlbit": file_path},keys=["algorithm","base"])



    # Adicione as CPDs ao modelo
    for cpd in cpds:
        melhor_model.add_cpds(cpd)

    # Escreva o modelo no formato XMLBIF
    writer = XMLBIFWriter(melhor_model).write_xmlbif(file_path)

    print(f"O arquivo XMLBIF foi gerado com sucesso em: {file_path}")