# Imports
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# From
from pandas import ExcelWriter
from pandas import ExcelFile
from PIL    import Image
from io     import BytesIO

# Configurando o tema do seaborn
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# Função para ler os dados
@st.cache_data()
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return pd.read_excel(file_data)

# Função para filtrar com multiseleção de categorias
@st.cache_data()
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Função para converter o DataFrame para CSV
@st.cache_data()
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter o DataFrame para Excel
@st.cache_data()
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# Criando os caminhos relativos dos arquivos de imagem
current_directory = os.path.dirname(os.path.realpath(__file__))
image_bank = "telmarketing_icon.png"
image_path_banking= os.path.join(current_directory, image_bank)
image_icon = "Bank-Branding.jpg"
image_path_icon = os.path.join(current_directory, image_icon)

# Função principal
def main():
    # Configuração inicial da aplicação
    st.set_page_config(page_title='Telemarketing analysis',
                        page_icon=Image.open(image_path_banking),  # Atualize com o caminho da sua imagem
                        layout="wide",
                        initial_sidebar_state='expanded'
                        )

    # Título principal da aplicação
    st.write('# Telemarketing analysis')
    st.markdown("---")
    
    # Apresenta a imagem na barra lateral da aplicação
    st.sidebar.image(Image.open(image_path_icon))  # Atualize com o caminho da sua imagem
    
    # Carregar arquivos na barra lateral da aplicação
    st.sidebar.markdown("## Carregar arquivos")
    data_file_1 = st.sidebar.file_uploader("Dados Bank marketing", type=['csv', 'xlsx'])

    # Verificar se o arquivo foi carregado
    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write("### Dados carregados")
        st.write(bank.head())
        
        with st.sidebar.form(key='my_form'):
            # Selecionar o tipo de gráfico
            graph_type = st.radio("Selecione o tipo de gráfico", ('Barras', 'Pizza'))

            # Idades no dataframe
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Idades', min_value=min_age, max_value=max_age, value=(min_age, max_age), step=1)

            # Default
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected = st.multiselect('Default', default_list, ['all'])

            # Lista de profissões disponíveis no dataframe
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected = st.multiselect('Profissões', jobs_list, ['all'])

            # Lista de estado civil
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected = st.multiselect('Estado civil', marital_list, ['all'])

            # Lista de financiamento imobiliário
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected = st.multiselect('Financiamento imobiliário', housing_list, ['all'])

            # Possui empréstimo
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected = st.multiselect("Empréstimo", loan_list, ['all'])

            # Meio de contato feito
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected = st.multiselect("Meio de contato", contact_list, ['all'])

            # Mês em que o contato foi feito
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected = st.multiselect("Mês", month_list, ['all'])

            # Dia da semana
            day_of_the_week_list = bank.day_of_week.unique().tolist()
            day_of_the_week_list.append('all')
            day_of_week_selected = st.multiselect("Dia da semana", day_of_the_week_list, ['all'])

            # Aplicação de filtros de seleção
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                    .pipe(multiselect_filter, 'job', jobs_selected)
                    .pipe(multiselect_filter, 'marital', marital_selected)
                    .pipe(multiselect_filter, 'housing', housing_selected)
                    .pipe(multiselect_filter, 'loan', loan_selected)
                    .pipe(multiselect_filter, 'contact', contact_selected)
                    .pipe(multiselect_filter, 'month', month_selected)
                    .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
                    .pipe(multiselect_filter, 'default', default_selected)
            )

            submit_button = st.form_submit_button(label='Filtrar')  # Botão para aplicar os filtros selecionados

        # Botões de download
        st.write('## Após filtros')
        st.write(bank.head())

        df_xlsx = to_excel(bank)
        st.download_button(label='Download em Excel', data=df_xlsx, file_name='bank_filtered.xlsx')
        st.markdown("---")

        # PLOTS
        # Plotando o gráfico do tipo barra
        if graph_type == 'Barras':
            fig, ax = plt.subplots(1, 2, figsize=(10, 6))
            bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame() * 100
            bank_raw_target_perc = bank_raw_target_perc.sort_index()

            try:
                bank_target_perc = bank.y.value_counts(normalize=True).to_frame() * 100
                bank_target_perc = bank_target_perc.sort_index()
            except Exception as e:
                st.error('Erro ao filtrar os dados')

            col1, col2 = st.columns(2)

            df_xlsx = to_excel(bank_raw_target_perc)
            col1.write('### Proporção original')
            col1.write(bank_raw_target_perc)
            col1.download_button(label='Download original em Excel', data=df_xlsx, file_name='bank_raw_target_perc.xlsx')

            df_xlsx = to_excel(bank_target_perc)
            col2.write('### Proporção após filtro')
            col2.write(bank_target_perc)
            col2.download_button(label='Download filtrado em Excel', data=df_xlsx, file_name='bank_target_perc.xlsx')

            col1.subheader('Dados brutos')
            col2.subheader('Dados filtrados')

            sns.barplot(x=bank_raw_target_perc.index, y='proportion', data=bank_raw_target_perc, ax=ax[0])
            ax[0].bar_label(ax[0].containers[0])

            sns.barplot(x=bank_target_perc.index, y='proportion', data=bank_target_perc, ax=ax[1])
            ax[1].bar_label(ax[1].containers[0])

        # Plotando o gráfico do tipo pizza
        else:
            fig, ax = plt.subplots(1, 2, figsize=(10, 6))

            bank_target_perc = bank.y.value_counts(normalize=True).to_frame() * 100
            bank_target_perc = bank_target_perc.sort_index()
            bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame() * 100
            bank_raw_target_perc = bank_raw_target_perc.sort_index()
            
            col1, col2 = st.columns(2)

            df_xlsx = to_excel(bank_raw_target_perc)
            col1.write('### Proporção original')
            col1.write(bank_raw_target_perc)
            col1.download_button(label='Download original em Excel', data=df_xlsx, file_name='bank_raw_target_perc.xlsx')

            df_xlsx = to_excel(bank_target_perc)
            col2.write('### Proporção após filtro')
            col2.write(bank_target_perc)
            col2.download_button(label='Download filtrado em Excel', data=df_xlsx, file_name='bank_target_perc.xlsx')

            col1.subheader('Dados brutos')
            col2.subheader('Dados filtrados')

            bank_raw_target_perc.plot(kind='pie', autopct='%.2f', y='proportion', ax=ax[0])
            ax[0].set_title('Dados brutos', fontweight="bold")

            bank_target_perc.plot(kind='pie', autopct='%.2f', y='proportion', ax=ax[1])
            ax[1].set_title('Dados filtrados', fontweight="bold")

        st.pyplot(fig)

if __name__ == '__main__':
    main()
