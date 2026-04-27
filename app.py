import streamlit as st
from ultralytics import YOLO, RTDETR
from PIL import Image
import os
import sys
import pathlib
import platform

# ==========================================
# 0. SYSTEM FIXES
# ==========================================
# Fix for PosixPath issue on Windows (common error)
if platform.system() == 'Windows':
    pathlib.PosixPath = pathlib.WindowsPath

# ==========================================
# 1. APP CONFIGURATION
# ==========================================
st.set_page_config(page_title="NeuroWaste Sorting AI", page_icon="♻️", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main {background-color: #f5f5f5;}
    h1 {color: #2e7d32;}
    .stButton>button {background-color: #2e7d32; color: white; border-radius: 8px;}
    div[data-testid="stSidebar"] {background-color: #e8f5e9;}
    </style>
    """, unsafe_allow_html=True)

st.title("♻️ NeuroWaste: Intelligent Waste Sorting System")
st.markdown("### Industrial-Grade Real-Time Detection for Recyclables")

# ==========================================
# 2. SIDEBAR (CONTROLS)
# ==========================================
st.sidebar.header("⚙️ Control Panel")

# A. Model Selection
# Ensure your 'models' folder exists and contains these files!
model_dir = os.path.abspath("models")

model_dict = {
    "RT-DETR (Your Custom Model)": os.path.join(model_dir, "rtdetr_l_waste_v1.pt"), # <--- ADDED HERE
    "YOLO11 Small (Best Balance)": os.path.join(model_dir, "yolo11s_best.pt"),
    "YOLO11 Nano (Fastest)": os.path.join(model_dir, "yolo11n_waste26_best.pt"),
    "YOLOv8 Medium (Highly Accurate)": os.path.join(model_dir, "yolov8sbest.pt"),
    "RT-DETR (Stock TACO)": os.path.join(model_dir, "rtdetr_l_taco_best.pt"),
    "YOLOv8 Nano": os.path.join(model_dir, "YOLOv8 Nano.pt")
}

# Auto-detect available models
available_models = {k: v for k, v in model_dict.items() if os.path.exists(v)}

if not available_models:
    st.error(f"❌ No models found in '{model_dir}' folder.")
    st.warning(f"Please copy your 'rtdetr_l_waste_v1.pt' file into the 'models' folder.")
    st.stop()
    
selected_model_name = st.sidebar.selectbox("Select AI Model", list(available_models.keys()))

# B. Confidence Slider
conf_thres = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.05)

# ==========================================
# 3. MODEL LOADING FUNCTION
# ==========================================
@st.cache_resource
def load_model(model_path):
    try:
        # Convert to string and normalize path for cross-platform compatibility
        model_path_str = str(model_path).replace("\\", "/")
        
        # Check architecture type
        if "rtdetr" in model_path_str.lower():
            # Load RT-DETR Model
            return RTDETR(model_path_str)
        else:
            # Load YOLO Model
            return YOLO(model_path_str)
            
    except Exception as e:
        st.error(f"Error loading model: {e}")
        raise e

# Load the selected model
try:
    model_path = available_models[selected_model_name]
    st.sidebar.text(f"Loading: {os.path.basename(model_path)}...")
    model = load_model(model_path)
    st.sidebar.success(f"✅ Active: {selected_model_name}")
    
except Exception as e:
    st.sidebar.error(f"❌ Crash: {str(e)}")
    st.stop()

# ==========================================
# 4. IMAGE UPLOAD & INFERENCE
# ==========================================
uploaded_file = st.file_uploader("Upload Conveyor Belt Image", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    # 1. Display Original
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

    # 2. Run Inference Button
    if st.button("🔍 Analyze Waste"):
        with st.spinner("Running Neural Network..."):
            try:
                # Run Inference
                results = model.predict(image, conf=conf_thres)
                
                # Plot Results (Draw boxes)
                res_plotted = results[0].plot()
                
                # Extract Metrics
                speed = results[0].speed['inference']
                count = len(results[0].boxes)
                
                # 3. Display Result
                with col2:
                    st.subheader("AI Detection Result")
                    st.image(res_plotted, caption=f"Detected {count} items in {speed:.1f}ms", use_container_width=True)
                
                # 4. Report Section (Professional Data)
                st.markdown("---")
                st.success(f"**Performance Metrics:** Inference Time: `{speed:.1f}ms` | Throughput: `{1000/speed:.1f} FPS` | Objects Found: `{count}`")
                
                # Show detected classes list
                if count > 0:
                    detected_classes = [results[0].names[int(box.cls)] for box in results[0].boxes]
                    st.info(f"**Detected Items:** {', '.join(set(detected_classes))}")
                    
            except Exception as e:
                st.error(f"Inference Error: {e}")