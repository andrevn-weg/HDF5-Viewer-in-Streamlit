import streamlit as st
import h5py
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from datetime import datetime

# # Configuração da página
# st.set_page_config(
#     page_title="Séries Temporais - HDF5 Viewer",
#     layout="wide",
#     page_icon="⏱️"
# )

# CSS customizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #2E86C1, #48C9B0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .section-header {
        background: #f0f2f6;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2E86C1;
        margin: 1rem 0;
    }
    .info-box {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">⏱️ Análise de Séries Temporais</h1>', unsafe_allow_html=True)

# Sidebar com controles
with st.sidebar:
    st.header("🎛️ Configurações")
    
    # Controles de visualização
    chart_height = st.slider("Altura do Gráfico", 300, 800, 500)
    show_grid = st.checkbox("Mostrar Grade", value=True)
    line_width = st.slider("Espessura da Linha", 1, 5, 2)
    
    # Controles de dados
    st.subheader("📊 Controles de Dados")
    use_sample_limit = st.checkbox("Limitar Amostras", value=False)
    if use_sample_limit:
        max_samples = st.number_input(
            "Máximo de amostras", 
            min_value=100, 
            max_value=50000, 
            value=5000,
            step=500
        )

# Função para encontrar datasets temporais
def find_temporal_datasets(h5obj, prefix=""):
    """Encontra datasets 2D onde primeira coluna é tempo e demais são dados"""
    temporal_datasets = []
    
    for key in h5obj:
        path = f"{prefix}/{key}" if prefix else key
        item = h5obj[key]
        
        if isinstance(item, h5py.Dataset):
            # Verifica se é 2D e tem pelo menos 2 colunas
            if item.ndim == 2 and item.shape[1] >= 2:
                # Verifica se parece ser dados temporais
                try:
                    data_sample = item[:min(100, item.shape[0]), :]
                    # Primeira coluna deve ser crescente (assumindo tempo)
                    if np.all(np.diff(data_sample[:, 0]) >= 0):
                        temporal_datasets.append({
                            'path': path,
                            'shape': item.shape,
                            'dtype': str(item.dtype),
                            'channels': item.shape[1] - 1  # Excluindo coluna tempo
                        })
                except:
                    pass
        elif isinstance(item, h5py.Group):
            temporal_datasets.extend(find_temporal_datasets(item, path))
    
    return temporal_datasets

def get_channel_names(dataset, dataset_path):
    """Gera nomes para os canais baseado nos atributos ou padrão"""
    channel_names = []
    
    # Tenta obter nomes dos atributos
    if 'channel_names' in dataset.attrs:
        try:
            names = dataset.attrs['channel_names']
            if isinstance(names, (list, np.ndarray)):
                channel_names = [str(name) for name in names]
        except:
            pass
    
    # Se não conseguiu obter nomes, gera nomes padrão
    if not channel_names:
        num_channels = dataset.shape[1] - 1
        channel_names = [f"Canal {i+1}" for i in range(num_channels)]
    
    return channel_names

def create_time_series_plot(time_data, channels_data, channel_names, selected_channels):
    """Cria gráfico de séries temporais interativo"""
    fig = go.Figure()
    
    for i, channel_name in enumerate(selected_channels):
        channel_idx = channel_names.index(channel_name)
        fig.add_trace(go.Scatter(
            x=time_data,
            y=channels_data[:, channel_idx],
            mode='lines',
            name=channel_name,
            line=dict(width=line_width),
            hovertemplate=f'<b>{channel_name}</b><br>' +
                         'Tempo: %{x}<br>' +
                         'Valor: %{y}<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title="Séries Temporais - Canais Selecionados",
        xaxis_title="Tempo",
        yaxis_title="Valor",
        hovermode='x unified',
        showlegend=True,
        height=chart_height,
        xaxis=dict(showgrid=show_grid),
        yaxis=dict(showgrid=show_grid),
        template="plotly_white"
    )
    
    return fig

def calculate_statistics(data, channel_names):
    """Calcula estatísticas básicas dos canais"""
    stats_data = []
    
    for i, channel_name in enumerate(channel_names):
        channel_data = data[:, i]
        stats_data.append({
            'Canal': channel_name,
            'Média': np.mean(channel_data),
            'Desvio Padrão': np.std(channel_data),
            'Mínimo': np.min(channel_data),
            'Máximo': np.max(channel_data),
            'Mediana': np.median(channel_data),
            'Variância': np.var(channel_data)
        })
    
    return pd.DataFrame(stats_data)

# Seção principal
st.markdown('<div class="section-header"><h2>📁 Upload do Arquivo HDF5</h2></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Selecione um arquivo HDF5 para análise de séries temporais", 
    type=["h5", "hdf5"],
    help="O arquivo deve conter datasets 2D onde a primeira coluna representa o tempo"
)

if uploaded_file is not None:
    # Salva arquivo temporariamente
    with open("temp_temporal.h5", "wb") as f:
        f.write(uploaded_file.read())
    
    # Abre arquivo HDF5
    with h5py.File("temp_temporal.h5", "r") as hdf:
        
        # Encontra datasets temporais
        temporal_datasets = find_temporal_datasets(hdf)
        
        if not temporal_datasets:
            st.error("❌ Nenhum dataset temporal encontrado no arquivo!")
            st.info("📝 Datasets temporais devem ser 2D com primeira coluna crescente (tempo)")
        else:
            st.success(f"✅ Encontrados {len(temporal_datasets)} datasets temporais no arquivo")
            
            # Seção de seleção de dataset
            st.markdown('<div class="section-header"><h2>🎯 Seleção do Dataset</h2></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Lista datasets encontrados
                dataset_options = []
                for ds in temporal_datasets:
                    label = f"{ds['path']} ({ds['channels']} canais, {ds['shape'][0]} amostras)"
                    dataset_options.append(label)
                
                selected_dataset_idx = st.selectbox(
                    "Escolha o dataset para análise:",
                    range(len(dataset_options)),
                    format_func=lambda x: dataset_options[x]
                )
                
                selected_dataset_info = temporal_datasets[selected_dataset_idx]
                dataset_path = selected_dataset_info['path']
                
                # Informações do dataset
                st.markdown("**Informações do Dataset:**")
                st.write(f"📊 Shape: {selected_dataset_info['shape']}")
                st.write(f"🔢 Tipo: {selected_dataset_info['dtype']}")
                st.write(f"📈 Canais: {selected_dataset_info['channels']}")
            
            with col2:
                # Carrega dados do dataset selecionado
                dataset = hdf[dataset_path]
                
                # Aplicar limite de amostras se habilitado
                if use_sample_limit and dataset.shape[0] > max_samples:
                    data = dataset[:max_samples, :]
                    st.info(f"📊 Exibindo {max_samples} de {dataset.shape[0]} amostras")
                else:
                    data = dataset[()]
                
                # Separar tempo e canais
                time_column = data[:, 0]
                channels_data = data[:, 1:]
                
                # Obter nomes dos canais
                channel_names = get_channel_names(dataset, dataset_path)
                
                # Seleção de canais
                st.markdown('<div class="section-header"><h3>🎛️ Seleção de Canais</h3></div>', unsafe_allow_html=True)
                
                selected_channels = st.multiselect(
                    "Escolha os canais para visualização:",
                    options=channel_names,
                    default=channel_names[:min(3, len(channel_names))],
                    help="Selecione um ou mais canais para análise"
                )
                
                if selected_channels:
                    # Seção de visualização
                    st.markdown('<div class="section-header"><h2>📈 Visualização</h2></div>', unsafe_allow_html=True)
                    
                    # Criar gráfico
                    fig = create_time_series_plot(time_column, channels_data, channel_names, selected_channels)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Seção de estatísticas
                    st.markdown('<div class="section-header"><h2>📊 Estatísticas</h2></div>', unsafe_allow_html=True)
                    
                    # Filtrar dados dos canais selecionados
                    selected_indices = [channel_names.index(ch) for ch in selected_channels]
                    selected_data = channels_data[:, selected_indices]
                    
                    # Calcular estatísticas
                    stats_df = calculate_statistics(selected_data, selected_channels)
                    
                    # Exibir estatísticas em colunas
                    col_stats1, col_stats2 = st.columns(2)
                    
                    with col_stats1:
                        st.subheader("📋 Resumo Estatístico")
                        st.dataframe(stats_df.round(4), use_container_width=True)
                    
                    with col_stats2:
                        st.subheader("📊 Métricas Principais")
                        for _, row in stats_df.iterrows():
                            st.metric(
                                label=f"{row['Canal']} - Média",
                                value=f"{row['Média']:.4f}",
                                delta=f"σ = {row['Desvio Padrão']:.4f}"
                            )
                    
                    # Seção de download
                    st.markdown('<div class="section-header"><h2>💾 Download dos Dados</h2></div>', unsafe_allow_html=True)
                    
                    col_down1, col_down2 = st.columns(2)
                    
                    with col_down1:
                        # Preparar dados para download
                        download_data = np.column_stack([time_column, selected_data])
                        download_columns = ['Tempo'] + selected_channels
                        download_df = pd.DataFrame(download_data, columns=download_columns)
                        
                        csv = download_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Dados Selecionados (CSV)",
                            data=csv,
                            file_name=f"series_temporais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    with col_down2:
                        # Download das estatísticas
                        stats_csv = stats_df.to_csv(index=False)
                        st.download_button(
                            label="📊 Download Estatísticas (CSV)",
                            data=stats_csv,
                            file_name=f"estatisticas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    # Seção de atributos
                    st.markdown('<div class="section-header"><h2>🏷️ Atributos do Dataset</h2></div>', unsafe_allow_html=True)
                    
                    if dataset.attrs:
                        attr_data = {}
                        for key in dataset.attrs.keys():
                            value = dataset.attrs[key]
                            if isinstance(value, bytes):
                                value = value.decode("utf-8")
                            elif isinstance(value, np.ndarray):
                                value = value.tolist()
                            attr_data[key] = str(value)
                        
                        attr_df = pd.DataFrame(attr_data.items(), columns=["Atributo", "Valor"])
                        st.dataframe(attr_df, use_container_width=True)
                        
                        # Download dos atributos
                        attr_csv = attr_df.to_csv(index=False)
                        st.download_button(
                            label="🏷️ Download Atributos (CSV)",
                            data=attr_csv,
                            file_name=f"atributos_{dataset_path.replace('/', '_')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("ℹ️ Nenhum atributo encontrado para este dataset")
                
                else:
                    st.warning("⚠️ Selecione pelo menos um canal para visualização")
    
    # Limpeza do arquivo temporário
    if os.path.exists("temp_temporal.h5"):
        os.remove("temp_temporal.h5")

else:
    # Página de boas-vindas
    st.markdown("""
    <div class="info-box">
    <h3>🚀 Bem-vindo à Análise de Séries Temporais!</h3>
    
    Esta ferramenta permite analisar séries temporais armazenadas em arquivos HDF5.
    
    <b>Características suportadas:</b>
    <ul>
        <li>📊 <b>Datasets 2D</b> onde a primeira coluna representa o tempo</li>
        <li>📈 <b>Múltiplos canais</b> de dados (colunas 2 em diante)</li>
        <li>🎯 <b>Seleção interativa</b> de canais para visualização</li>
        <li>📋 <b>Estatísticas detalhadas</b> por canal</li>
        <li>💾 <b>Export de dados</b> e resultados</li>
        <li>🏷️ <b>Visualização de metadados</b> e atributos</li>
    </ul>
    
    <b>Para começar:</b> Faça upload de um arquivo HDF5 acima!
    </div>
    """, unsafe_allow_html=True)
    
    # Dicas de uso
    with st.expander("💡 Dicas de Uso", expanded=False):
        st.markdown("""
        - **Formato esperado:** Datasets 2D com primeira coluna crescente (tempo)
        - **Performance:** Use o limitador de amostras para arquivos grandes
        - **Visualização:** Ajuste altura e espessura das linhas na barra lateral
        - **Análise:** Compare múltiplos canais selecionando-os simultaneamente
        - **Export:** Baixe dados filtrados e estatísticas em formato CSV
        """)

# Footer
st.markdown("---")
st.markdown("*Desenvolvido para análise de séries temporais em arquivos HDF5 📊*")
