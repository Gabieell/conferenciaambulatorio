import pandas as pd
import streamlit as st

# Função para encontrar pendências
def encontrar_pendencias(agenda_df, pagamento_df):
    # Mergulhar com base no número de atendimento
    pendencias_df = agenda_df.merge(pagamento_df[['Atendimento']], how='left', on='Atendimento', indicator=True)
    
    # Adicionar verificação pelo nome do paciente se o número de atendimento não for encontrado
    pendencias_df['Paciente'] = pendencias_df['Paciente'].fillna('')
    for idx, row in pendencias_df[pendencias_df['_merge'] == 'left_only'].iterrows():
        nome_paciente = row['Paciente']
        if nome_paciente:
            if pagamento_df['Paciente'].str.contains(nome_paciente, case=False, na=False).any():
                pendencias_df.at[idx, 'Paciente'] = nome_paciente

    # Filtrar apenas os registros que ainda não foram encontrados
    pendencias_df = pendencias_df[pendencias_df['_merge'] == 'left_only']
    
    # Segunda checagem para verificar se o nome do paciente já está na planilha de pagamento
    pendencias_df['Paciente'] = pendencias_df['Paciente'].fillna('')
    pendencias_df_final = pendencias_df.copy()
    for idx, row in pendencias_df.iterrows():
        nome_paciente = row['Paciente']
        if nome_paciente:
            if pagamento_df['Paciente'].str.contains(nome_paciente, case=False, na=False).any():
                pendencias_df_final = pendencias_df_final.drop(idx)
    
    # Selecionar apenas as colunas necessárias
    pendencias_df_final = pendencias_df_final[['Data', 'Atendimento', 'Paciente' , 'Classificação']]
    
    return pendencias_df_final

# Configuração da interface Streamlit
st.title("Sistema de Conferência de Pagamento Médico")
st.write("Desenvolvido por Gabrielle Carvalho")

# Carregar as planilhas
uploaded_file_agenda = st.file_uploader("Escolha a planilha de agenda", type="xlsx")
uploaded_file_pagamento = st.file_uploader("Escolha a planilha de pagamento", type="xlsx")

if uploaded_file_agenda and uploaded_file_pagamento:
    agenda_df = pd.read_excel(uploaded_file_agenda, sheet_name=None)
    pagamento_df = pd.read_excel(uploaded_file_pagamento)

    # Concatenar todas as abas da planilha de agenda em um único DataFrame
    agenda_df = pd.concat(agenda_df.values(), ignore_index=True)

    # Encontrar pendências
    pendencias_df = encontrar_pendencias(agenda_df, pagamento_df)

    # Mostrar as pendências no aplicativo
    st.write("Pendências encontradas:")
    st.dataframe(pendencias_df)

    # Permitir download da planilha de pendências
    pendencias_file = "pendencias.xlsx"
    pendencias_df.to_excel(pendencias_file, index=False)
    st.download_button(label="Baixar planilha de pendências", data=open(pendencias_file, 'rb').read(), file_name=pendencias_file)
else:
    st.write("Por favor, faça o upload das planilhas de agenda e pagamento.")
