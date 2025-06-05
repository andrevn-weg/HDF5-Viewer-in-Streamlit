import streamlit as st
import h5py
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="HDF5 Viewer", layout="wide")
st.title("📂 HDF5 Viewer in Streamlit")

# Step 1: Upload File
uploaded_file = st.file_uploader("Upload an HDF5 file", type=["h5", "hdf5"])
if uploaded_file is not None:
    # Save temporarily
    with open("temp_file.h5", "wb") as f:
        f.write(uploaded_file.read())

    # Open file with h5py
    with h5py.File("temp_file.h5", "r") as hdf:

        # Step 2: List all paths recursively
        def list_items(h5obj, prefix=""):
            items = []
            for key in h5obj:
                path = f"{prefix}/{key}" if prefix else key
                items.append(path)
                if isinstance(h5obj[key], h5py.Group):
                    items.extend(list_items(h5obj[key], path))
            return items

        st.subheader("📁 File Structure")
        all_paths = list_items(hdf)
        selected_path = st.selectbox("Select a group or dataset", all_paths)

        if selected_path in hdf:
            obj = hdf[selected_path]

            # Step 3: Dataset Preview
            if isinstance(obj, h5py.Dataset):
                st.subheader("🧮 Dataset Preview")

                try:
                    data = obj[()]
                    if isinstance(data, np.ndarray):
                        shape = data.shape
                        st.caption(f"Shape: {shape}, Dtype: {data.dtype}")

                        # Show limited data for large arrays
                        if data.ndim == 1:
                            df = pd.DataFrame(data, columns=[selected_path.split('/')[-1]])
                        elif data.ndim == 2:
                            df = pd.DataFrame(data)
                        else:
                            df = pd.DataFrame({f"Index {i}": v for i, v in enumerate(data.flatten()[:10])}, index=[0])

                        st.dataframe(df)
                    else:
                        st.write(data)
                except Exception as e:
                    st.error(f"Error reading dataset: {e}")

            # Step 4: Attribute Display + CSV Export
            st.subheader("🏷️ Attributes")

            if hasattr(obj, "attrs") and obj.attrs:
                attr_keys = list(obj.attrs.keys())

                selected_attrs = st.multiselect(
                    "Choose attributes to display:",
                    options=attr_keys,
                    default=attr_keys
                )

                if selected_attrs:
                    attr_data = {
                        key: obj.attrs[key].decode("utf-8") if isinstance(obj.attrs[key], bytes) else obj.attrs[key]
                        for key in selected_attrs
                    }

                    df_attrs = pd.DataFrame(attr_data.items(), columns=["Attribute", "Value"])
                    st.dataframe(df_attrs)

                    csv = df_attrs.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download Selected Attributes as CSV",
                        data=csv,
                        file_name=f"{selected_path.replace('/', '_')}_attributes.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("Please select at least one attribute.")
            else:
                st.warning("No attributes found.")
