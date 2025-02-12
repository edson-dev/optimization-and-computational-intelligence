import pandas as pd
import time
from sklearn.ensemble import RandomForestClassifier
from boruta import BorutaPy
from sklearn.preprocessing import LabelEncoder
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import K2Score, BayesianEstimator

from sql import RepositorySQL


def boruta_feature_order(data_path, target_column, estimator=10):
    # Separar os dados em características (X) e alvo (y)
    X = data.drop(columns=[target_column])
    y = data[target_column]

    # Inicializar um classificador Random Forest
    rf = RandomForestClassifier(n_estimators=estimator, n_jobs=-1)

    # Inicializar o Boruta
    boruta_selector = BorutaPy(rf, n_estimators='auto', verbose=2)

    # Ajustar o Boruta aos dados
    boruta_selector.fit(X.values, y.values)
    print("Boruta inicializado com sucesso")

    selected_features = X.columns[boruta_selector.support_]
    unselected_features = X.columns[~boruta_selector.support_]

    all_features = [target_column] + list(selected_features) + list(unselected_features)
    df_reordered = data[all_features]

    return df_reordered


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
    file_name = "asia"#"hepartwo"
     # Variáveis para acompanhar a melhor estrutura, melhor ordem, melhor score e a target_column relacionada
    melhor_estrutura = None
    melhor_ordem = None
    melhor_score = float('-inf')
    melhor_target = None

    # Carregar os dados do CSV
    data = pd.read_csv(f"data/{file_name}.csv")# caminho para o arquivo CSV
    # Mapear os valores nominais para números inteiros únicos
    data = data.apply(LabelEncoder().fit_transform)
    variables = list(data.columns)

    print("DataFrame original:")
    print(list(data))



    start_time = time.time()

    # Loop através de cada coluna, considerando-a como a coluna alvo uma vez
    for target_column in variables:
        if target_column == "target_column":
            continue

        df_reordered = boruta_feature_order(data, target_column)
        variable_target = list(df_reordered)
        estrutura, model, score = k2(df_reordered, 4)

        # Imprimir a ordem, estrutura e score para cada coluna alvo
        print(f'Ordem gerada com a feature {target_column}: {variable_target}')
        print(f'Estrutura gerada: {estrutura}')
        print(f'Score obtido: {score}')
        print()

        # Verificar se esta estrutura é a melhor até agora
        if score > melhor_score:
            melhor_estrutura = estrutura
            melhor_ordem = list(df_reordered)
            melhor_score = score
            melhor_target = target_column
            melhor_model = model

    # Tabular as CPDs para o melhor modelo gerado
    cpds = tabular_cpd(melhor_model, df_reordered)

    end_time = time.time()
    execution_time = end_time - start_time

    from pgmpy.readwrite import XMLBIFWriter

    # Especifique o caminho do arquivo onde deseja salvar o arquivo XMLBIF
    file_path = f"result/{file_name}_boruta_best.xmlbif"

    from pgmpy.readwrite import XMLBIFWriter
    # Especifique o caminho do arquivo onde deseja salvar o arquivo XMLBIF
    file_path = f"result/{file_name}_boruta_best.xmlbif"

    # Abre o arquivo em modo de escrita
    with open(f"result/{file_name}_boruta_best.txt", "w") as arquivo:
        # Escreve os prints no arquivo
        arquivo.write(f'Melhor ordem gerada com a feature ({melhor_target}): {melhor_ordem}\n')
        arquivo.write(f'Estrutura dessa ordem: {melhor_estrutura}\n')
        arquivo.write(f'Score obtido dessa ordem: {melhor_score}\n')
        arquivo.write(f'Tempo: {execution_time}\n')
    with RepositorySQL("sqlite:///./masters.db") as repo:
        a = repo.upsert("optimization", {"algorithm": "boruta","base": file_name,"feature": melhor_target, "order": str(melhor_ordem), "structure": str(melhor_estrutura), "score": melhor_score, "time": execution_time, "xmlbit": file_path},keys=["algorithm","base"])


    # Adicione as CPDs ao modelo
    for cpd in cpds:
        melhor_model.add_cpds(cpd)

    # Escreva o modelo no formato XMLBIF
    writer = XMLBIFWriter(melhor_model).write_xmlbif(file_path)

    print(f"O arquivo XMLBIF foi gerado com sucesso em: {file_path}")
