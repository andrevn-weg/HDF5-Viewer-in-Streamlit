# 📊 Advanced HDF5 Viewer & Analyzer

A powerful web-based HDF5 file explorer and analyzer built with Streamlit. This enhanced version provides comprehensive data visualization and multi-channel analysis capabilities.

## 🚀 Features

### Core Functionality
- 📁 **Upload and explore** HDF5 files with intuitive navigation
- 📊 **Interactive visualizations** using Plotly for dynamic charts
- 🔍 **Multi-dataset selection** for comparative analysis
- 📈 **Multiple chart types**: Line plots, histograms, scatter plots, box plots, heatmaps
- 📋 **Statistical analysis** with detailed summary statistics
- 💾 **Data export** in CSV format with download buttons

### Advanced Features
- 🎯 **Smart data filtering** with sample limiting for large datasets
- 🔄 **Multi-channel comparison** for simultaneous analysis
- 🌡️ **Correlation analysis** with interactive heatmaps
- 📊 **Rich metadata display** with organized attribute viewing
- 🎨 **Modern UI** with custom styling and responsive layout
- ⚡ **Performance optimization** for handling large datasets

### Visualization Options
- **Time Series Plots**: Interactive line charts with zoom and pan
- **Distribution Analysis**: Histograms with customizable bins
- **Correlation Matrices**: Heatmaps showing channel relationships
- **Statistical Summaries**: Comprehensive data statistics
- **Multi-Dataset Overlays**: Compare multiple datasets simultaneously

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd HDF5-Viewer-in-Streamlit

# Install requirements
pip install -r requirements.txt
```

## 🎮 Usage

### Quick Start
```bash
# Run the application
streamlit run streamlit_app.py

# Or use the provided batch file (Windows)
run_app.bat
```

### Creating Sample Data
```bash
# Generate sample HDF5 file for testing
python create_sample_data.py
```

This creates `sample_data.h5` with:
- Multiple sensor channels (sine, cosine, mixed signals)
- Environmental data (temperature, pressure)
- Rich metadata and attributes
- Time vectors and multi-channel datasets

### Using the Application

1. **Upload File**: Use the file uploader to select your HDF5 file
2. **Select Datasets**: Choose one or multiple datasets from the dropdown
3. **Customize Visualization**: Select chart types and adjust settings
4. **Analyze Data**: Explore time series, distributions, and correlations
5. **Export Results**: Download data and visualizations as needed

## 🛠️ Dependencies

- `streamlit` - Web application framework
- `h5py` - HDF5 file handling
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `plotly` - Interactive visualizations
- `matplotlib` - Additional plotting capabilities
- `seaborn` - Statistical data visualization

## 📁 Project Structure

```
HDF5-Viewer-in-Streamlit/
├── streamlit_app.py          # Main application
├── requirements.txt          # Python dependencies
├── create_sample_data.py     # Sample data generator
├── run_app.bat              # Windows startup script
└── README.md                # This file
```

## 🎯 Use Cases

- **Scientific Data Analysis**: Explore experimental datasets with multiple channels
- **Engineering Applications**: Analyze sensor data and measurement results
- **Data Quality Assessment**: Visualize data distributions and identify anomalies
- **Comparative Studies**: Compare multiple datasets side by side
- **Educational Purposes**: Learn about HDF5 file structure and data analysis

## 🔧 Customization

The application supports various customization options:
- Adjustable chart heights
- Configurable data sampling limits
- Toggle-able sections (raw data, statistics)
- Multiple visualization themes
- Exportable results in multiple formats

## 📈 Performance Tips

- Use sample limiting for datasets with >10,000 points
- Select specific channels rather than entire file for better performance
- Export processed data for offline analysis
- Use correlation analysis for identifying relationships in multi-channel data

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional visualization types
- Real-time data streaming
- Advanced filtering options
- Custom export formats
- Database integration

## 📄 License

This project is open source and available under the MIT License.
