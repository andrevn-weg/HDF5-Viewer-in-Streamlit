import os 

import os

# Directory structure for the HDF5 Viewer Streamlit app
project_name = "streamlit_hdf5_viewer"
base_path = f"/mnt/data/{project_name}"

# Folder and file structure
structure = {
    "": ["README.md", "requirements.txt", "streamlit_app.py"],
    "utils": ["hdf_utils.py", "__init__.py"],
    ".streamlit": ["config.toml"]
}

# Create the directories and files
for folder, files in structure.items():
    dir_path = os.path.join(base_path, folder)
    os.makedirs(dir_path, exist_ok=True)
    for file in files:
        open(os.path.join(dir_path, file), "w").close()

base_path
