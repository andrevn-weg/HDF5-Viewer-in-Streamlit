import streamlit as st
import h5py
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

# st.set_page_config(page_title="HDF5 Viewer", layout="wide", page_icon="📊")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">� Advanced HDF5 Viewer & Analyzer</h1>', unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.header("🎛️ Controls")
    show_raw_data = st.checkbox("Show Raw Data", value=True)
    show_statistics = st.checkbox("Show Statistics", value=True)
    chart_height = st.slider("Chart Height", 300, 800, 500)

# Helper functions
def list_datasets_only(h5obj, prefix=""):
    """List only datasets (not groups) recursively"""
    datasets = []
    for key in h5obj:
        path = f"{prefix}/{key}" if prefix else key
        if isinstance(h5obj[key], h5py.Dataset):
            datasets.append(path)
        elif isinstance(h5obj[key], h5py.Group):
            datasets.extend(list_datasets_only(h5obj[key], path))
    return datasets

def get_dataset_info(dataset):
    """Get detailed information about a dataset"""
    return {
        'Shape': dataset.shape,
        'Dtype': str(dataset.dtype),
        'Size': dataset.size,
        'Dimensionality': dataset.ndim,
        'Compression': dataset.compression,
        'Chunks': dataset.chunks
    }

def is_plottable(data):
    """Check if data can be plotted"""
    if not isinstance(data, np.ndarray):
        return False
    if data.dtype.kind not in ['i', 'u', 'f', 'c']:  # int, uint, float, complex
        return False
    if data.ndim > 2:
        return False
    return True

def create_time_series_plot(data, column_names, title="Time Series Data"):
    """Create interactive time series plot"""
    fig = go.Figure()
    
    if data.ndim == 1:
        fig.add_trace(go.Scatter(
            y=data,
            mode='lines',
            name=column_names[0] if column_names else 'Channel 1',
            line=dict(width=2)
        ))
    else:
        for i, col_name in enumerate(column_names):
            if i < data.shape[1]:
                fig.add_trace(go.Scatter(
                    y=data[:, i],
                    mode='lines',
                    name=col_name,
                    line=dict(width=2)
                ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Sample Index",
        yaxis_title="Value",
        hovermode='x unified',
        showlegend=True,
        height=chart_height
    )
    
    return fig

def create_histogram_plot(data, column_names):
    """Create histogram plot for selected columns"""
    num_cols = min(len(column_names), 4)  # Limit to 4 columns max for better display
    
    fig = make_subplots(
        rows=1, cols=num_cols,
        subplot_titles=column_names[:num_cols],
        shared_yaxes=True
    )
    
    for i in range(num_cols):
        col_name = column_names[i]
        if data.ndim == 1:
            hist_data = data
        else:
            hist_data = data[:, i] if i < data.shape[1] else data[:, 0]
        
        fig.add_trace(
            go.Histogram(x=hist_data, name=col_name, nbinsx=50, showlegend=False),
            row=1, col=i+1
        )
    
    fig.update_layout(
        title="Data Distribution",
        height=chart_height
    )
    
    return fig

def create_correlation_heatmap(data, column_names):
    """Create correlation heatmap for multi-channel data"""
    if data.ndim != 2 or data.shape[1] < 2:
        return None
    
    df = pd.DataFrame(data, columns=column_names)
    correlation_matrix = df.corr()
    
    fig = px.imshow(
        correlation_matrix,
        title="Channel Correlation Matrix",
        color_continuous_scale="RdBu_r",
        aspect="auto",
        height=chart_height
    )
    
    return fig

# Main application
uploaded_file = st.file_uploader("📁 Upload an HDF5 file", type=["h5", "hdf5"])

if uploaded_file is not None:
    # Save temporarily
    with open("temp_file.h5", "wb") as f:
        f.write(uploaded_file.read())

    # Open file with h5py
    with h5py.File("temp_file.h5", "r") as hdf:
        
        # Get all datasets
        all_datasets = list_datasets_only(hdf)
        
        if not all_datasets:
            st.error("No datasets found in the HDF5 file.")
        else:
            st.success(f"Found {len(all_datasets)} datasets in the file")
            
            # Create two columns for layout
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("📊 Dataset Selection")
                
                # Multi-select for datasets
                selected_datasets = st.multiselect(
                    "Select datasets to analyze:",
                    options=all_datasets,
                    default=[all_datasets[0]] if all_datasets else [],
                    help="You can select multiple datasets for comparison"
                )
                
                if selected_datasets:
                    # Analysis options
                    st.subheader("🔧 Analysis Options")
                    plot_type = st.selectbox(
                        "Chart Type:",
                        ["Line Plot", "Histogram", "Scatter Plot", "Box Plot"]
                    )
                    
                    # Data filtering options
                    st.subheader("🎯 Data Filtering")
                    use_sample_limit = st.checkbox("Limit samples", value=True)
                    if use_sample_limit:
                        max_samples = st.number_input("Max samples to display", 
                                                    min_value=100, 
                                                    max_value=100000, 
                                                    value=10000,
                                                    step=1000)
            
            with col2:
                if selected_datasets:
                    # Process selected datasets
                    datasets_data = {}
                    datasets_info = {}
                    
                    for dataset_path in selected_datasets:
                        try:
                            dataset = hdf[dataset_path]
                            data = dataset[()]
                            
                            # Apply sample limit if enabled
                            if use_sample_limit and isinstance(data, np.ndarray) and data.size > max_samples:
                                if data.ndim == 1:
                                    data = data[:max_samples]
                                elif data.ndim == 2:
                                    data = data[:max_samples, :]
                            
                            datasets_data[dataset_path] = data
                            datasets_info[dataset_path] = get_dataset_info(dataset)
                            
                        except Exception as e:
                            st.error(f"Error loading dataset {dataset_path}: {e}")
                    
                    if datasets_data:
                        # Dataset Information
                        st.subheader("📋 Dataset Information")
                        info_cols = st.columns(min(len(datasets_data), 3))
                        
                        for i, (path, info) in enumerate(datasets_info.items()):
                            with info_cols[i % 3]:
                                with st.container():
                                    st.markdown(f"**{path.split('/')[-1]}**")
                                    st.metric("Shape", str(info['Shape']))
                                    st.metric("Size", f"{info['Size']:,}")
                                    st.caption(f"Type: {info['Dtype']}")
                        
                        # Plotting section
                        st.subheader("📈 Data Visualization")
                        
                        # Handle single vs multiple datasets
                        if len(selected_datasets) == 1:
                            dataset_path = selected_datasets[0]
                            data = datasets_data[dataset_path]
                            
                            if is_plottable(data):                                # Generate column names and channel selection
                                if data.ndim == 1:
                                    column_names = [dataset_path.split('/')[-1]]
                                    available_channels = column_names
                                else:
                                    available_channels = [f"Channel_{i+1}" for i in range(data.shape[1])]
                                    column_names = available_channels
                                
                                # Channel selection for multi-dimensional data
                                selected_channels = []
                                if data.ndim == 2 and data.shape[1] > 1:
                                    st.subheader("🎯 Channel Selection")
                                    selected_channels = st.multiselect(
                                        "Select channels to display:",
                                        options=available_channels,
                                        default=available_channels[:min(5, len(available_channels))],  # Default to first 5 channels
                                        help="Select one or more channels for visualization"
                                    )
                                    
                                    if not selected_channels:
                                        st.warning("Please select at least one channel to display")
                                        selected_channels = [available_channels[0]]
                                    
                                    # Filter data based on selected channels
                                    channel_indices = [available_channels.index(ch) for ch in selected_channels]
                                    filtered_data = data[:, channel_indices]
                                    column_names = selected_channels
                                else:
                                    filtered_data = data
                                    selected_channels = column_names
                                  # Create tabs for different visualizations
                                plot_tabs = st.tabs(["📊 Time Series", "📈 Histogram", "🔥 Heatmap", "📋 Statistics"])
                                
                                with plot_tabs[0]:
                                    if plot_type == "Line Plot":
                                        fig = create_time_series_plot(filtered_data, column_names, f"Time Series: {dataset_path}")
                                        st.plotly_chart(fig, use_container_width=True)
                                    elif plot_type == "Scatter Plot" and filtered_data.ndim == 2 and filtered_data.shape[1] >= 2:
                                        fig = px.scatter(x=filtered_data[:, 0], y=filtered_data[:, 1], 
                                                       title=f"Scatter Plot: {dataset_path}",
                                                       labels={'x': column_names[0], 'y': column_names[1]})
                                        fig.update_layout(height=chart_height)
                                        st.plotly_chart(fig, use_container_width=True)
                                    elif plot_type == "Box Plot":
                                        df = pd.DataFrame(filtered_data, columns=column_names if filtered_data.ndim == 2 else [column_names[0]])
                                        fig = px.box(df.melt(), x='variable', y='value', 
                                                   title=f"Box Plot: {dataset_path}")
                                        fig.update_layout(height=chart_height)
                                        st.plotly_chart(fig, use_container_width=True)
                                
                                with plot_tabs[1]:
                                    fig = create_histogram_plot(filtered_data, column_names)
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                with plot_tabs[2]:
                                    if filtered_data.ndim == 2 and filtered_data.shape[1] > 1:
                                        fig = create_correlation_heatmap(filtered_data, column_names)
                                        if fig:
                                            st.plotly_chart(fig, use_container_width=True)
                                    else:
                                        st.info("Correlation heatmap requires multi-channel data")
                                
                                with plot_tabs[3]:
                                    if show_statistics:
                                        df = pd.DataFrame(filtered_data, columns=column_names if filtered_data.ndim == 2 else [column_names[0]])
                                        st.subheader("📊 Statistical Summary")
                                        st.dataframe(df.describe(), use_container_width=True)
                                        
                                        # Additional statistics
                                        stat_col1, stat_col2 = st.columns(2)
                                        with stat_col1:
                                            st.metric("Total Samples", len(df))
                                            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                                        with stat_col2:
                                            st.metric("Columns", len(df.columns))
                                            st.metric("Missing Values", df.isnull().sum().sum())
                            else:
                                st.warning("Selected dataset is not suitable for plotting")
                                st.write("Data preview:", data)
                        
                        else:
                            # Multiple datasets comparison
                            st.subheader("🔄 Multi-Dataset Comparison")
                            
                            # Create comparison plots
                            fig = go.Figure()
                            
                            for dataset_path in selected_datasets:
                                data = datasets_data[dataset_path]
                                if is_plottable(data) and data.ndim == 1:
                                    fig.add_trace(go.Scatter(
                                        y=data,
                                        mode='lines',
                                        name=dataset_path.split('/')[-1],
                                        line=dict(width=2)
                                    ))
                            
                            fig.update_layout(
                                title="Multi-Dataset Comparison",
                                xaxis_title="Sample Index",
                                yaxis_title="Value",
                                hovermode='x unified',
                                height=chart_height
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Raw data display
                        if show_raw_data:
                            st.subheader("📄 Raw Data Preview")
                            for dataset_path in selected_datasets:
                                with st.expander(f"Data from {dataset_path}"):
                                    data = datasets_data[dataset_path]
                                    if isinstance(data, np.ndarray):
                                        if data.ndim == 1:
                                            df = pd.DataFrame(data, columns=[dataset_path.split('/')[-1]])
                                        elif data.ndim == 2:
                                            df = pd.DataFrame(data, columns=[f"Col_{i}" for i in range(data.shape[1])])
                                        else:
                                            df = pd.DataFrame({"Values": data.flatten()[:1000]})  # Flatten for display
                                        
                                        st.dataframe(df.head(1000), use_container_width=True)
                                        
                                        # Download button
                                        csv = df.to_csv(index=False)
                                        st.download_button(
                                            label=f"⬇️ Download {dataset_path.split('/')[-1]} as CSV",
                                            data=csv,
                                            file_name=f"{dataset_path.replace('/', '_')}.csv",
                                            mime="text/csv"
                                        )
                                    else:
                                        st.write(data)
                        
                        # Attributes section
                        st.subheader("🏷️ Dataset Attributes")
                        attr_tabs = st.tabs([path.split('/')[-1] for path in selected_datasets])
                        
                        for i, dataset_path in enumerate(selected_datasets):
                            with attr_tabs[i]:
                                obj = hdf[dataset_path]
                                if hasattr(obj, "attrs") and obj.attrs:
                                    attr_data = {}
                                    for key in obj.attrs.keys():
                                        value = obj.attrs[key]
                                        if isinstance(value, bytes):
                                            value = value.decode("utf-8")
                                        attr_data[key] = value
                                    
                                    df_attrs = pd.DataFrame(attr_data.items(), columns=["Attribute", "Value"])
                                    st.dataframe(df_attrs, use_container_width=True)
                                    
                                    # Download attributes
                                    csv = df_attrs.to_csv(index=False)
                                    st.download_button(
                                        label=f"⬇️ Download Attributes",
                                        data=csv,
                                        file_name=f"{dataset_path.replace('/', '_')}_attributes.csv",
                                        mime="text/csv",
                                        key=f"attr_{i}"
                                    )
                                else:
                                    st.info("No attributes found for this dataset")
                else:
                    st.info("👆 Please select at least one dataset to analyze")
    
    # Cleanup
    if os.path.exists("temp_file.h5"):
        os.remove("temp_file.h5")

else:
    # Welcome message when no file is uploaded
    st.markdown("""
    ### 🚀 Welcome to the Advanced HDF5 Viewer!
    
    This application allows you to:
    - 📊 **Visualize** HDF5 datasets with interactive charts
    - 🔍 **Analyze** multiple channels simultaneously  
    - 📈 **Compare** different datasets side by side
    - 📋 **Export** data and visualizations
    - 🎯 **Filter** and sample large datasets
    
    **Get started by uploading an HDF5 file above!**
    """)
    
    # Example section
    with st.expander("💡 Tips for best results"):
        st.markdown("""
        - **Large files**: Use the sample limit feature to improve performance
        - **Multiple channels**: Select multiple datasets for comparison
        - **Different chart types**: Try different visualization options
        - **Export options**: Download your data as CSV or save visualizations
        """)

# Footer
st.markdown("---")
st.markdown("*Built with ❤️ using Streamlit and Plotly*")
