import pandas as pd
from sklearn.preprocessing import LabelEncoder
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import K2Score, BayesianEstimator
import time

import viz
from sql import RepositorySQL


def correlacao_spearman(data, target):
    # Calcula a correlação de Spearman entre a coluna alvo e todas as outras colunas
    correlacoes = data.corr(method='spearman')
    target_correlacao = correlacoes[target]
    # Ordena as colunas com base na correlação em ordem decrescente
    correlacoes_ordenadas = target_correlacao.abs().sort_values(ascending=False)

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


def execute(file_name:str, db:RepositorySQL = RepositorySQL("sqlite:///./networks.db")):
    # Variáveis para acompanhar a melhor estrutura, melhor ordem, melhor score e a target_column relacionada
    melhor_estrutura = None
    melhor_ordem = None
    melhor_score = float('-inf')
    melhor_target = None
    data = pd.read_csv(f'data/{file_name}.csv')  # caminho do dataset
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
        df_ordenado = correlacao_spearman(data, target)
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
    from pgmpy.readwrite import XMLBIFWriter
    # Especifique o caminho do arquivo onde deseja salvar o arquivo XMLBIF
    file_path = f"result/{file_name}_spearman.xml.bif"
    # Adicione as CPDs ao modelo
    for cpd in cpds:
        melhor_model.add_cpds(cpd)
    # Escreva o modelo no formato XMLBIF
    w = XMLBIFWriter(melhor_model)
    w.write_xmlbif(file_path)
    # P2
    with db as repo:
        a = repo.upsert("optimization", {"algorithm": "spearman", "base": file_name, "feature": melhor_target,
                                         "order": str(melhor_ordem), "structure": str(melhor_estrutura),
                                         "score": float(melhor_score), "time": execution_time, "xmlbif": file_path,"file": w.__str__(),
                                         "dag": viz.file(melhor_ordem, melhor_estrutura)},
                        keys=["algorithm", "base"])


    print(f"O arquivo XMLBIF foi gerado com sucesso em: {file_path}")


if __name__ == "__main__":
    from main import bases
    for base in bases:
        execute(base)
