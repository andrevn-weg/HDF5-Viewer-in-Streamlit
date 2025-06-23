import h5py
import numpy as np
import pandas as pd

def create_sample_hdf5_file(filename="sample_multichannel_data.h5"):
    """Create a sample HDF5 file with multiple datasets and channels for testing"""
    
    # Create synthetic data
    np.random.seed(42)
    time_points = 10000
    time_axis = np.linspace(0, 10, time_points)
    
    # Create different types of data
    # 1. Single channel sine wave
    single_channel = np.sin(2 * np.pi * 1.5 * time_axis) + 0.1 * np.random.randn(time_points)
    
    # 2. Multi-channel sensor data (accelerometer simulation)
    num_channels = 8
    multi_channel_data = np.zeros((time_points, num_channels))
    for i in range(num_channels):
        freq = 0.5 + i * 0.3  # Different frequencies for each channel
        amplitude = 1.0 + i * 0.2  # Different amplitudes
        multi_channel_data[:, i] = amplitude * np.sin(2 * np.pi * freq * time_axis) + 0.1 * np.random.randn(time_points)
    
    # 3. Temperature data (multiple sensors)
    temp_sensors = 4
    temperature_data = np.zeros((time_points, temp_sensors))
    base_temp = [20, 25, 30, 35]  # Different base temperatures
    for i in range(temp_sensors):
        temperature_data[:, i] = base_temp[i] + 5 * np.sin(2 * np.pi * 0.1 * time_axis) + 0.5 * np.random.randn(time_points)
    
    # 4. Vibration data (3-axis accelerometer)
    vibration_3axis = np.zeros((time_points, 3))
    vibration_3axis[:, 0] = 0.5 * np.sin(2 * np.pi * 10 * time_axis) + 0.1 * np.random.randn(time_points)  # X-axis
    vibration_3axis[:, 1] = 0.3 * np.cos(2 * np.pi * 15 * time_axis) + 0.1 * np.random.randn(time_points)  # Y-axis  
    vibration_3axis[:, 2] = 0.2 * np.sin(2 * np.pi * 20 * time_axis) + 0.05 * np.random.randn(time_points)  # Z-axis
    
    # 5. Pressure data (multiple locations)
    pressure_sensors = 6
    pressure_data = np.zeros((time_points, pressure_sensors))
    for i in range(pressure_sensors):
        base_pressure = 1013.25 + i * 10  # Different base pressures
        pressure_data[:, i] = base_pressure + 20 * np.sin(2 * np.pi * 0.05 * time_axis) + 2 * np.random.randn(time_points)
    
    # Create HDF5 file
    with h5py.File(filename, 'w') as f:
        # Create groups for organization
        sensors_group = f.create_group('sensors')
        signals_group = f.create_group('signals')
        environmental_group = f.create_group('environmental')
        
        # Add datasets with attributes
        # Single channel data
        ds1 = signals_group.create_dataset('sine_wave', data=single_channel)
        ds1.attrs['description'] = 'Single channel sine wave with noise'
        ds1.attrs['frequency'] = 1.5
        ds1.attrs['sampling_rate'] = time_points / 10.0
        ds1.attrs['units'] = 'V'
        
        # Multi-channel sensor data
        ds2 = sensors_group.create_dataset('multi_sensor', data=multi_channel_data)
        ds2.attrs['description'] = 'Multi-channel sensor data'
        ds2.attrs['channels'] = num_channels
        ds2.attrs['sampling_rate'] = time_points / 10.0
        ds2.attrs['units'] = 'mV'
        ds2.attrs['channel_names'] = [f'Sensor_{i+1}' for i in range(num_channels)]
        
        # Temperature data
        ds3 = environmental_group.create_dataset('temperature', data=temperature_data)
        ds3.attrs['description'] = 'Temperature measurements from multiple sensors'
        ds3.attrs['units'] = 'Celsius'
        ds3.attrs['sensor_locations'] = ['Room_A', 'Room_B', 'Room_C', 'Room_D']
        
        # Vibration data
        ds4 = sensors_group.create_dataset('vibration_3axis', data=vibration_3axis)
        ds4.attrs['description'] = '3-axis accelerometer data'
        ds4.attrs['units'] = 'g'
        ds4.attrs['axes'] = ['X', 'Y', 'Z']
        ds4.attrs['sampling_rate'] = time_points / 10.0
        
        # Pressure data
        ds5 = environmental_group.create_dataset('pressure', data=pressure_data)
        ds5.attrs['description'] = 'Pressure measurements from multiple locations'
        ds5.attrs['units'] = 'hPa'
        ds5.attrs['sensor_count'] = pressure_sensors
        
        # Add time axis as reference
        time_ds = f.create_dataset('time_axis', data=time_axis)
        time_ds.attrs['description'] = 'Time axis for all measurements'
        time_ds.attrs['units'] = 'seconds'
        
        # Add some metadata at file level
        f.attrs['created_by'] = 'HDF5 Viewer Sample Data Generator'
        f.attrs['version'] = '1.0'
        f.attrs['total_samples'] = time_points
        f.attrs['duration'] = 10.0
    
    print(f"Created sample HDF5 file: {filename}")
    print(f"File contains {time_points} samples across multiple datasets")
    print("Datasets created:")
    print("- signals/sine_wave: Single channel sine wave")
    print(f"- sensors/multi_sensor: {num_channels} channel sensor data")
    print(f"- environmental/temperature: {temp_sensors} temperature sensors")
    print("- sensors/vibration_3axis: 3-axis accelerometer data")
    print(f"- environmental/pressure: {pressure_sensors} pressure sensors")
    print("- time_axis: Time reference")

if __name__ == "__main__":
    create_sample_hdf5_file("sample_multichannel_data.h5")
    print("\nSample file created successfully!")
    print("You can now upload this file to the HDF5 Viewer to test multi-channel functionality.")
