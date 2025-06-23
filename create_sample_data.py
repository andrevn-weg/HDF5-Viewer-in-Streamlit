import h5py
import numpy as np
import pandas as pd

def create_sample_hdf5():
    """Create a sample HDF5 file with multiple datasets for testing"""
    
    # Generate sample data
    np.random.seed(42)
    time_points = 10000
    
    # Time series data
    time = np.linspace(0, 10, time_points)
    
    # Channel 1: Sine wave with noise
    channel1 = np.sin(2 * np.pi * 1.0 * time) + 0.1 * np.random.randn(time_points)
    
    # Channel 2: Cosine wave with different frequency
    channel2 = np.cos(2 * np.pi * 2.5 * time) + 0.1 * np.random.randn(time_points)
    
    # Channel 3: Mixed signal
    channel3 = 0.5 * np.sin(2 * np.pi * 0.5 * time) + 0.3 * np.cos(2 * np.pi * 3.0 * time) + 0.1 * np.random.randn(time_points)
    
    # Multi-channel matrix
    multi_channel_data = np.column_stack([channel1, channel2, channel3])
    
    # Temperature data (example)
    temperature = 20 + 5 * np.sin(2 * np.pi * 0.1 * time) + np.random.randn(time_points) * 0.5
    
    # Pressure data (example)
    pressure = 1013 + 10 * np.sin(2 * np.pi * 0.05 * time) + np.random.randn(time_points) * 2
    
    # Create HDF5 file
    with h5py.File('sample_data.h5', 'w') as f:
        
        # Create groups
        sensors_group = f.create_group('sensors')
        signals_group = f.create_group('signals')
        metadata_group = f.create_group('metadata')
        
        # Add individual channel datasets
        channel1_ds = sensors_group.create_dataset('channel_1', data=channel1)
        channel1_ds.attrs['description'] = 'Sine wave signal with noise'
        channel1_ds.attrs['units'] = 'V'
        channel1_ds.attrs['sampling_rate'] = 1000.0
        channel1_ds.attrs['sensor_type'] = 'voltage'
        
        channel2_ds = sensors_group.create_dataset('channel_2', data=channel2)
        channel2_ds.attrs['description'] = 'Cosine wave signal'
        channel2_ds.attrs['units'] = 'V'
        channel2_ds.attrs['sampling_rate'] = 1000.0
        channel2_ds.attrs['sensor_type'] = 'voltage'
        
        channel3_ds = sensors_group.create_dataset('channel_3', data=channel3)
        channel3_ds.attrs['description'] = 'Mixed frequency signal'
        channel3_ds.attrs['units'] = 'V'
        channel3_ds.attrs['sampling_rate'] = 1000.0
        channel3_ds.attrs['sensor_type'] = 'voltage'
        
        # Add multi-channel dataset
        multi_ds = signals_group.create_dataset('multi_channel', data=multi_channel_data)
        multi_ds.attrs['description'] = 'Multi-channel sensor data'
        multi_ds.attrs['channels'] = ['Channel 1', 'Channel 2', 'Channel 3']
        multi_ds.attrs['units'] = 'V'
        multi_ds.attrs['sampling_rate'] = 1000.0
        
        # Add environmental data
        temp_ds = sensors_group.create_dataset('temperature', data=temperature)
        temp_ds.attrs['description'] = 'Temperature measurements'
        temp_ds.attrs['units'] = '°C'
        temp_ds.attrs['sensor_type'] = 'temperature'
        temp_ds.attrs['location'] = 'Room A'
        
        pressure_ds = sensors_group.create_dataset('pressure', data=pressure)
        pressure_ds.attrs['description'] = 'Atmospheric pressure'
        pressure_ds.attrs['units'] = 'hPa'
        pressure_ds.attrs['sensor_type'] = 'pressure'
        pressure_ds.attrs['location'] = 'Room A'
        
        # Add time vector
        time_ds = f.create_dataset('time', data=time)
        time_ds.attrs['description'] = 'Time vector'
        time_ds.attrs['units'] = 'seconds'
        
        # Add metadata
        metadata_group.attrs['experiment_name'] = 'Sample Data Collection'
        metadata_group.attrs['date'] = '2025-06-23'
        metadata_group.attrs['operator'] = 'HDF5 Viewer Demo'
        metadata_group.attrs['equipment'] = 'Simulated Data Generator'
        metadata_group.attrs['notes'] = 'This is sample data for testing the HDF5 viewer'
        
        # Add some statistics
        stats_group = metadata_group.create_group('statistics')
        stats_group.attrs['total_samples'] = time_points
        stats_group.attrs['duration_seconds'] = time[-1] - time[0]
        stats_group.attrs['channels_count'] = 3
    
    print("✅ Sample HDF5 file 'sample_data.h5' created successfully!")
    print("📊 File contains:")
    print("   - 3 individual channel datasets")
    print("   - 1 multi-channel dataset")
    print("   - Temperature and pressure data")
    print("   - Time vector")
    print("   - Rich metadata and attributes")
    print("\n🚀 You can now upload this file to the HDF5 Viewer!")

if __name__ == "__main__":
    create_sample_hdf5()
