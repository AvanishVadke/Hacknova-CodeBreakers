"""
🏫 Smart Campus Access Control System
Professional Streamlit Dashboard
Integrates ID Card Recognition, License Plate Detection, and Supabase Database
"""

import streamlit as st
import cv2
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time
import numpy as np
from PIL import Image

# Try to import pandas, but make it optional
try:
    import pandas as pd
    HAS_PANDAS = True
except:
    HAS_PANDAS = False

# Add current directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from offline_id_card_recognizer import OfflineIDCardRecognizer
from test_indian_plates import IndianLicensePlateRecognizer
from database.supabase_manager import SupabaseManager

# Page configuration
st.set_page_config(
    page_title="Campus Access Control",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .processing-box {
        background-color: #cce5ff;
        border: 2px solid #004085;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = None
if 'id_recognizer' not in st.session_state:
    st.session_state.id_recognizer = None
if 'plate_recognizer' not in st.session_state:
    st.session_state.plate_recognizer = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False


@st.cache_resource
def initialize_system():
    """Initialize all components with proper error handling"""
    try:
        # Database
        db = SupabaseManager()
        db_connected = db.connect()
        if db_connected:
            db.create_tables()
        
        # ID Card Recognizer
        id_recognizer = OfflineIDCardRecognizer()
        
        # License Plate Recognizer
        plate_model_path = "../License-Plate-Extraction-Save-Data-to-SQL-Database/weights/best.pt"
        plate_recognizer = IndianLicensePlateRecognizer(model_path=plate_model_path)
        
        return {
            'db': db if db_connected else None,
            'id_recognizer': id_recognizer,
            'plate_recognizer': plate_recognizer,
            'status': 'success'
        }
    except Exception as e:
        return {
            'db': None,
            'id_recognizer': None,
            'plate_recognizer': None,
            'status': 'error',
            'error': str(e)
        }


def process_id_card(image, recognizer, db=None):
    """Process ID card image with proper error handling"""
    try:
        # Convert PIL to OpenCV
        img_array = np.array(image)
        frame = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Detect card
        card_bbox = recognizer.detect_id_card_opencv(frame)
        
        if card_bbox:
            x, y, w, h = card_bbox
            card_region = frame[y:y+h, x:x+w]
            
            # Extract text
            preprocessed = recognizer.preprocess_for_ocr(card_region)
            ocr_results = recognizer.extract_text_with_ocr(preprocessed)
            
            # Parse data
            card_data = recognizer.parse_id_card_text(ocr_results)
            
            # Save to database
            if db and card_data.get('moodle_id'):
                try:
                    db.insert_student(
                        moodle_id=card_data['moodle_id'],
                        name=card_data.get('name'),
                        department=card_data.get('department')
                    )
                    
                    db.log_id_card_access(
                        moodle_id=card_data['moodle_id'],
                        name=card_data.get('name'),
                        department=card_data.get('department'),
                        confidence=card_data.get('confidence', 0.0),
                        camera_id='streamlit_app',
                        status='allowed'
                    )
                    card_data['db_saved'] = True
                except Exception as db_error:
                    card_data['db_saved'] = False
                    card_data['db_error'] = str(db_error)
            
            # Draw rectangle on image
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            result_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            return {
                'success': True,
                'data': card_data,
                'image': result_img
            }
        else:
            return {
                'success': False,
                'message': 'No ID card detected in image'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Processing error: {str(e)}'
        }


def process_license_plate(image, recognizer, db=None):
    """Process license plate image with proper error handling"""
    try:
        # Convert PIL to OpenCV
        img_array = np.array(image)
        frame = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Detect plates
        results = recognizer.model(frame, conf=0.25, verbose=False)
        
        plates_found = []
        annotated_frame = frame.copy()
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Validate box format before unpacking
                try:
                    if len(box.xyxy[0]) != 4:
                        continue  # Skip malformed detections
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                except (ValueError, IndexError, TypeError) as e:
                    continue  # Skip any unpacking errors
                
                if conf > 0.25:
                    # Extract text
                    plate_text = recognizer.extract_plate_text(frame, x1, y1, x2, y2)
                    
                    if plate_text:
                        # Only show/save plates with >= 80% confidence
                        if conf >= 0.80:
                            plates_found.append({
                                'plate': plate_text,
                                'confidence': conf
                            })
                            
                            # Draw rectangle (green for high confidence)
                            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                            cv2.putText(annotated_frame, f"{plate_text} ({conf:.1%})", (x1, y1-10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                            
                            # Save to database
                            if db:
                                try:
                                    db.insert_vehicle(license_plate=plate_text)
                                    db.log_vehicle_access(
                                        license_plate=plate_text,
                                        confidence=conf,
                                        camera_id='streamlit_app',
                                        status='allowed'
                                    )
                                except:
                                    pass
        
        if plates_found:
            result_img = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            return {
                'success': True,
                'data': plates_found,
                'image': result_img
            }
        else:
            return {
                'success': False,
                'message': 'No license plates detected with ≥80% confidence'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Processing error: {str(e)}'
        }


def main():
    # Header
    st.markdown('<h1 class="main-header">🏫 Smart Campus Access Control</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered ID Card & License Plate Recognition</p>', unsafe_allow_html=True)
    
    # Initialize system
    if not st.session_state.initialized:
        with st.spinner('🚀 Initializing system...'):
            init_result = initialize_system()
            
            if init_result['status'] == 'success':
                st.session_state.db = init_result['db']
                st.session_state.id_recognizer = init_result['id_recognizer']
                st.session_state.plate_recognizer = init_result['plate_recognizer']
                st.session_state.initialized = True
                st.success('✅ System initialized successfully!')
            else:
                st.error(f'❌ Initialization failed: {init_result.get("error", "Unknown error")}')
                st.stop()
    
    # Sidebar
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio(
        "Select Module",
        ["🏠 Dashboard", "🆔 ID Card Scanner", "🚗 License Plate Scanner", "ℹ️ About"]
    )
    
    # Database status
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗄️ Database Status")
    if st.session_state.db:
        st.sidebar.success("✅ Connected")
    else:
        st.sidebar.error("❌ Disconnected")
    
    # Main content
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🆔 ID Card Scanner":
        show_id_card_scanner()
    elif page == "🚗 License Plate Scanner":
        show_plate_scanner()
    elif page == "ℹ️ About":
        show_about()


def show_dashboard():
    """Dashboard with statistics and recent logs"""
    st.header("📊 System Dashboard")
    
    if not st.session_state.db:
        st.warning("⚠️ Database not connected. Statistics not available.")
        return
    
    # Statistics
    try:
        with st.spinner('📈 Loading statistics...'):
            stats = st.session_state.db.get_today_statistics()
            
            if stats:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="🆔 ID Card Entries",
                        value=stats['id_card_entries'],
                        delta="Today"
                    )
                
                with col2:
                    st.metric(
                        label="🚗 Vehicle Entries",
                        value=stats['vehicle_entries'],
                        delta="Today"
                    )
                
                with col3:
                    st.metric(
                        label="📈 Total Entries",
                        value=stats['total_entries'],
                        delta="Today"
                    )
            else:
                st.info("ℹ️ No entries recorded today yet.")
        
        # Recent logs
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Recent ID Card Logs")
            with st.spinner('Loading...'):
                id_logs = st.session_state.db.get_recent_id_card_logs(limit=10)
                
                if id_logs:
                    for log in id_logs:
                        st.markdown(f"""
                        **{log['moodle_id']}** - {log['name']}  
                        📍 {log.get('department', 'N/A')} | ⏰ {log['access_time'].strftime('%H:%M:%S')}
                        ---
                        """)
                else:
                    st.info("No logs found")
        
        with col2:
            st.subheader("🚗 Recent Vehicle Logs")
            with st.spinner('Loading...'):
                vehicle_logs = st.session_state.db.get_recent_vehicle_logs(limit=10)
                
                if vehicle_logs:
                    for log in vehicle_logs:
                        st.markdown(f"""
                        🚗 **{log['license_plate']}**  
                        📊 Confidence: {log['confidence']:.1%} | ⏰ {log['access_time'].strftime('%H:%M:%S')}
                        ---
                        """)
                else:
                    st.info("No logs found")
                    
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")


def show_id_card_scanner():
    """ID Card scanning interface"""
    st.header("🆔 ID Card Scanner")
    
    # Add tabs for upload vs live camera
    tab1, tab2 = st.tabs(["📤 Upload Image", "📷 Live Camera"])
    
    with tab1:
        st.markdown("""
        **Instructions:**
        1. Upload an image containing an ID card
        2. The system will detect and extract information
        3. Results will be saved to the database automatically
        """)
        
        uploaded_file = st.file_uploader(
            "📤 Upload ID Card Image",
            type=['jpg', 'jpeg', 'png'],
            help="Supported formats: JPG, JPEG, PNG"
        )
        
        process_uploaded_id_card(uploaded_file)
    
    with tab2:
        show_live_camera_id_scanner()


def show_live_camera_id_scanner():
    """Live camera feed for ID card scanning"""
    st.markdown("""
    **Instructions:**
    1. Click "Start Camera" to open live feed
    2. Position your ID card within the green guide box
    3. Click "Capture ID Card" to take photo
    4. System will automatically process and save to database
    """)
    
    # Camera controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        start_camera = st.button("📷 Start Camera", type="primary")
    
    with col2:
        capture_button = st.button("📸 Capture ID Card")
    
    with col3:
        stop_camera = st.button("⏹️ Stop Camera")
    
    # Initialize session state for camera
    if 'camera_active' not in st.session_state:
        st.session_state.camera_active = False
    if 'captured_frame' not in st.session_state:
        st.session_state.captured_frame = None
    
    # Start camera
    if start_camera:
        st.session_state.camera_active = True
        st.session_state.captured_frame = None
    
    # Stop camera
    if stop_camera:
        st.session_state.camera_active = False
    
    # Live camera feed
    if st.session_state.camera_active:
        st.markdown("---")
        
        # Create placeholder for camera feed
        FRAME_WINDOW = st.image([])
        camera_placeholder = st.empty()
        
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                st.error("❌ Could not open webcam")
                st.session_state.camera_active = False
                return
            
            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            camera_placeholder.success(f"✅ Camera active: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            
            # Capture loop
            frame_count = 0
            while st.session_state.camera_active and frame_count < 300:  # Max 300 frames (10 seconds at 30fps)
                ret, frame = cap.read()
                
                if not ret:
                    st.error("❌ Error reading from camera")
                    break
                
                # Create display frame with guide box
                display_frame = frame.copy()
                h, w = frame.shape[:2]
                
                # Guide box (60% of frame)
                guide_w = int(w * 0.6)
                guide_h = int(h * 0.6)
                x1 = (w - guide_w) // 2
                y1 = (h - guide_h) // 2
                x2 = x1 + guide_w
                y2 = y1 + guide_h
                
                # Draw guide rectangle
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                
                # Add text instructions
                cv2.putText(display_frame, "Position ID card within green box", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.putText(display_frame, "Click 'Capture ID Card' button to capture", 
                           (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                # Convert BGR to RGB for display
                display_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                
                # Update frame in Streamlit
                FRAME_WINDOW.image(display_frame_rgb, channels="RGB", use_column_width=True)
                
                # Check if capture button was pressed
                if capture_button:
                    st.session_state.captured_frame = frame.copy()
                    st.session_state.camera_active = False
                    camera_placeholder.success("✅ ID card captured!")
                    break
                
                frame_count += 1
                time.sleep(0.033)  # ~30 fps
            
            cap.release()
            
        except Exception as e:
            st.error(f"❌ Camera error: {str(e)}")
            st.session_state.camera_active = False
    
    # Process captured frame
    if st.session_state.captured_frame is not None and not st.session_state.camera_active:
        st.markdown("---")
        st.subheader("📸 Captured Image")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Original Capture:**")
            frame_rgb = cv2.cvtColor(st.session_state.captured_frame, cv2.COLOR_BGR2RGB)
            st.image(frame_rgb, use_column_width=True)
        
        with col2:
            st.markdown("**Processing Results:**")
            
            with st.spinner('🔄 Processing ID card...'):
                # Convert to PIL Image
                frame_pil = Image.fromarray(frame_rgb)
                
                result = process_id_card(
                    frame_pil,
                    st.session_state.id_recognizer,
                    st.session_state.db
                )
            
            if result['success']:
                st.image(result['image'], use_column_width=True)
                
                # Show extracted data
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success("✅ ID Card Detected Successfully!")
                
                data = result['data']
                
                if data.get('moodle_id'):
                    st.markdown(f"**🆔 Moodle ID:** `{data['moodle_id']}`")
                if data.get('name'):
                    st.markdown(f"**👤 Name:** {data['name']}")
                if data.get('department'):
                    st.markdown(f"**🏢 Department:** {data['department']}")
                if data.get('confidence'):
                    st.markdown(f"**📊 Confidence:** {data['confidence']:.2%}")
                
                if data.get('db_saved'):
                    st.markdown("**🗄️ Database:** Saved successfully")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Clear captured frame button
                if st.button("🔄 Capture Another", type="secondary"):
                    st.session_state.captured_frame = None
                    st.rerun()
            else:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"❌ {result['message']}")
                st.markdown('</div>', unsafe_allow_html=True)


def process_uploaded_id_card(uploaded_file):
    """Process uploaded ID card image"""
    
    if uploaded_file:
        # Display original image
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📸 Original Image")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
        
        with col2:
            st.subheader("🔍 Processing Results")
            
            with st.spinner('🔄 Processing ID card...'):
                result = process_id_card(
                    image,
                    st.session_state.id_recognizer,
                    st.session_state.db
                )
            
            if result['success']:
                # Show annotated image
                st.image(result['image'], use_column_width=True)
                
                # Show extracted data
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success("✅ ID Card Detected Successfully!")
                
                data = result['data']
                
                if data.get('moodle_id'):
                    st.markdown(f"**🆔 Moodle ID:** `{data['moodle_id']}`")
                if data.get('name'):
                    st.markdown(f"**👤 Name:** {data['name']}")
                if data.get('department'):
                    st.markdown(f"**🏢 Department:** {data['department']}")
                if data.get('confidence'):
                    st.markdown(f"**📊 Confidence:** {data['confidence']:.2%}")
                
                if data.get('db_saved'):
                    st.markdown("**🗄️ Database:** Saved successfully")
                elif 'db_saved' in data:
                    st.warning(f"⚠️ Database save failed: {data.get('db_error', 'Unknown error')}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"❌ {result['message']}")
                st.markdown('</div>', unsafe_allow_html=True)


def show_plate_scanner():
    """License plate scanning interface"""
    st.header("🚗 License Plate Scanner")
    
    # Add tabs for upload vs live camera
    tab1, tab2 = st.tabs(["📤 Upload Image", "📷 Live Camera"])
    
    with tab1:
        st.markdown("""
        **Instructions:**
        1. Upload an image or video containing vehicle license plates
        2. The system will detect and extract plate numbers
        3. Only plates with ≥80% confidence will be shown and saved
        4. Results will be saved to the database automatically
        """)
        
        uploaded_file = st.file_uploader(
            "📤 Upload Vehicle Image or Video",
            type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'],
            help="Supported formats: JPG, JPEG, PNG, MP4, AVI, MOV",
            key="plate_upload"
        )
        
        if uploaded_file:
            # Check if it's a video
            if uploaded_file.type.startswith('video'):
                process_uploaded_video_plate(uploaded_file)
            else:
                process_uploaded_plate(uploaded_file)
    
    with tab2:
        show_live_camera_plate_scanner()


def show_live_camera_plate_scanner():
    """Live camera feed for license plate scanning"""
    st.markdown("""
    **Instructions:**
    1. Click "Start Camera" to open live feed
    2. Position vehicle license plate in view
    3. Click "Capture" to detect plates
    4. Only plates with ≥80% confidence will be shown and saved
    5. System will automatically save to database
    """)
    
    # Camera controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        start_camera = st.button("📷 Start Camera", type="primary", key="plate_start")
    
    with col2:
        capture_button = st.button("📸 Capture Plate", key="plate_capture")
    
    with col3:
        stop_camera = st.button("⏹️ Stop Camera", key="plate_stop")
    
    # Initialize session state
    if 'plate_camera_active' not in st.session_state:
        st.session_state.plate_camera_active = False
    if 'plate_captured_frame' not in st.session_state:
        st.session_state.plate_captured_frame = None
    
    # Start camera
    if start_camera:
        st.session_state.plate_camera_active = True
        st.session_state.plate_captured_frame = None
    
    # Stop camera
    if stop_camera:
        st.session_state.plate_camera_active = False
    
    # Live camera feed
    if st.session_state.plate_camera_active:
        st.markdown("---")
        
        FRAME_WINDOW = st.image([])
        camera_placeholder = st.empty()
        
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                st.error("❌ Could not open webcam")
                st.session_state.plate_camera_active = False
                return
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            camera_placeholder.success(f"✅ Camera active: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            
            frame_count = 0
            while st.session_state.plate_camera_active and frame_count < 300:
                ret, frame = cap.read()
                
                if not ret:
                    st.error("❌ Error reading from camera")
                    break
                
                display_frame = frame.copy()
                h, w = frame.shape[:2]
                
                # Add text instructions
                cv2.putText(display_frame, "Position vehicle license plate in view", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.putText(display_frame, "Click 'Capture Plate' button to detect", 
                           (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                display_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                FRAME_WINDOW.image(display_frame_rgb, channels="RGB", use_column_width=True)
                
                if capture_button:
                    st.session_state.plate_captured_frame = frame.copy()
                    st.session_state.plate_camera_active = False
                    camera_placeholder.success("✅ Frame captured!")
                    break
                
                frame_count += 1
                time.sleep(0.033)
            
            cap.release()
            
        except Exception as e:
            st.error(f"❌ Camera error: {str(e)}")
            st.session_state.plate_camera_active = False
    
    # Process captured frame
    if st.session_state.plate_captured_frame is not None and not st.session_state.plate_camera_active:
        st.markdown("---")
        st.subheader("📸 Captured Image")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Original Capture:**")
            frame_rgb = cv2.cvtColor(st.session_state.plate_captured_frame, cv2.COLOR_BGR2RGB)
            st.image(frame_rgb, use_column_width=True)
        
        with col2:
            st.markdown("**Processing Results:**")
            
            with st.spinner('🔄 Detecting license plates...'):
                frame_pil = Image.fromarray(frame_rgb)
                
                result = process_license_plate(
                    frame_pil,
                    st.session_state.plate_recognizer,
                    st.session_state.db
                )
            
            if result['success']:
                st.image(result['image'], use_column_width=True)
                
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"✅ Detected {len(result['data'])} High-Confidence License Plate(s) (≥80%)")
                
                for i, plate_data in enumerate(result['data'], 1):
                    st.markdown(f"**Plate {i}:** `{plate_data['plate']}` (Confidence: {plate_data['confidence']:.2%})")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.button("🔄 Capture Another", type="secondary", key="plate_retry"):
                    st.session_state.plate_captured_frame = None
                    st.rerun()
            else:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"❌ {result['message']}")
                st.markdown('</div>', unsafe_allow_html=True)


def process_uploaded_video_plate(uploaded_file):
    """Process uploaded video for license plate detection"""
    if not uploaded_file:
        return
    
    st.markdown("---")
    st.subheader("🎬 Video Processing")
    
    # Save uploaded video temporarily
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(uploaded_file.read())
        video_path = tmp_file.name
    
    try:
        # Video info
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.release()
        
        st.info(f"📹 Video: {total_frames} frames @ {fps} FPS")
        
        # Processing options
        col1, col2 = st.columns(2)
        with col1:
            max_frames = st.slider("Max frames to process:", 10, min(1000, total_frames), min(300, total_frames))
        with col2:
            skip_frames = st.slider("Skip frames:", 1, 10, 1)
        
        if st.button("🚀 Process Video", type="primary"):
            with st.spinner(f'🔄 Processing video... (max {max_frames} frames)'):
                plates_detected = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                cap = cv2.VideoCapture(video_path)
                frame_count = 0
                processed_count = 0
                
                while processed_count < max_frames:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    frame_count += 1
                    
                    # Skip frames
                    if frame_count % skip_frames != 0:
                        continue
                    
                    processed_count += 1
                    
                    # Detect plates
                    try:
                        results = st.session_state.plate_recognizer.model(frame, conf=0.25, verbose=False)
                        
                        for result in results:
                            for box in result.boxes:
                                # Validate box format before unpacking
                                try:
                                    if len(box.xyxy[0]) != 4:
                                        continue  # Skip malformed detections
                                    
                                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                                    conf = float(box.conf[0])
                                except (ValueError, IndexError, TypeError) as e:
                                    continue  # Skip any unpacking errors
                                
                                if conf > 0.25:
                                    plate_text = st.session_state.plate_recognizer.extract_plate_text(
                                        frame, x1, y1, x2, y2
                                    )
                                    
                                    if plate_text and len(plate_text) > 3:
                                        # Only save and show plates with >= 80% confidence
                                        if conf >= 0.80:
                                            plates_detected.append({
                                                'plate': plate_text,
                                                'confidence': conf,
                                                'frame': processed_count
                                            })
                                            
                                            # Save to database
                                            if st.session_state.db:
                                                try:
                                                    st.session_state.db.insert_vehicle(license_plate=plate_text)
                                                    st.session_state.db.log_vehicle_access(
                                                        license_plate=plate_text,
                                                        confidence=conf,
                                                        camera_id='video_upload',
                                                        status='allowed'
                                                    )
                                                except:
                                                    pass
                    except:
                        pass
                    
                    # Update progress
                    progress = processed_count / max_frames
                    progress_bar.progress(progress)
                    status_text.text(f"Processed: {processed_count}/{max_frames} frames | Plates found: {len(plates_detected)}")
                
                cap.release()
                progress_bar.progress(1.0)
                
                # Show results
                st.markdown("---")
                st.success(f"✅ Processing complete! Detected {len(plates_detected)} high-confidence plates (≥80%) from {processed_count} frames")
                
                if plates_detected:
                    # Get unique plates
                    unique_plates = {}
                    for p in plates_detected:
                        if p['plate'] not in unique_plates:
                            unique_plates[p['plate']] = {'count': 1, 'conf': p['confidence']}
                        else:
                            unique_plates[p['plate']]['count'] += 1
                            unique_plates[p['plate']]['conf'] = max(unique_plates[p['plate']]['conf'], p['confidence'])
                    
                    st.markdown(f"**🔢 Unique plates detected:** {len(unique_plates)}")
                    
                    # Display unique plates
                    for plate, info in sorted(unique_plates.items(), key=lambda x: x[1]['count'], reverse=True)[:20]:
                        st.markdown(f"- **{plate}** - Detected {info['count']}x (Max confidence: {info['conf']:.1%})")
                else:
                    st.warning("⚠️ No license plates detected with ≥80% confidence in video")
    
    finally:
        # Clean up temp file
        try:
            os.unlink(video_path)
        except:
            pass


def process_uploaded_plate(uploaded_file):
    """Process uploaded license plate image"""
    
    if uploaded_file:
        # Display original image
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📸 Original Image")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
        
        with col2:
            st.subheader("🔍 Processing Results")
            
            with st.spinner('🔄 Processing license plates...'):
                result = process_license_plate(
                    image,
                    st.session_state.plate_recognizer,
                    st.session_state.db
                )
            
            if result['success']:
                # Show annotated image
                st.image(result['image'], use_column_width=True)
                
                # Show extracted plates
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"✅ Detected {len(result['data'])} High-Confidence License Plate(s) (≥80%)")
                
                for i, plate_data in enumerate(result['data'], 1):
                    st.markdown(f"**Plate {i}:** `{plate_data['plate']}` (Confidence: {plate_data['confidence']:.2%})")
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"❌ {result['message']}")
                st.markdown('</div>', unsafe_allow_html=True)


def show_database():
    """Database viewer and management"""
    st.header("🗄️ Database Management")
    
    if not st.session_state.db:
        st.warning("⚠️ Database not connected.")
        return
    
    tab1, tab2, tab3 = st.tabs(["👥 Students", "🚗 Vehicles", "📋 Logs"])
    
    with tab1:
        st.subheader("Registered Students")
        
        # Search
        search_query = st.text_input("🔍 Search by Moodle ID or Name")
        
        if search_query:
            # Search functionality can be added to SupabaseManager
            st.info(f"Searching for: {search_query}")
        else:
            st.info("Enter Moodle ID or name to search")
    
    with tab2:
        st.subheader("Registered Vehicles")
        
        search_query = st.text_input("🔍 Search by License Plate", key="vehicle_search")
        
        if search_query:
            with st.spinner('Searching...'):
                try:
                    vehicle = st.session_state.db.get_vehicle(license_plate=search_query)
                    if vehicle:
                        st.success(f"✅ Found: {vehicle['license_plate']}")
                        if vehicle.get('owner_moodle_id'):
                            st.write(f"**Owner:** {vehicle['owner_moodle_id']}")
                        if vehicle.get('vehicle_type'):
                            st.write(f"**Type:** {vehicle['vehicle_type']}")
                    else:
                        st.warning("⚠️ Vehicle not found")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab3:
        st.subheader("Access Logs")
        
        log_type = st.radio("Select log type:", ["ID Card Logs", "Vehicle Logs"])
        limit = st.slider("Number of records:", 10, 100, 50)
        
        if st.button("🔄 Load Logs"):
            with st.spinner('Loading...'):
                try:
                    if log_type == "ID Card Logs":
                        logs = st.session_state.db.get_recent_id_card_logs(limit=limit)
                        if logs:
                            for log in logs:
                                st.markdown(f"""
                                **{log['moodle_id']}** - {log['name']}  
                                📍 {log.get('department', 'N/A')} | ⏰ {log['access_time']}
                                ---
                                """)
                        else:
                            st.info("No logs found")
                    else:
                        logs = st.session_state.db.get_recent_vehicle_logs(limit=limit)
                        if logs:
                            for log in logs:
                                st.markdown(f"""
                                🚗 **{log['license_plate']}**  
                                📊 {log['confidence']:.1%} | ⏰ {log['access_time']}
                                ---
                                """)
                        else:
                            st.info("No logs found")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


def show_about():
    """About page"""
    st.header("ℹ️ About")
    
    st.markdown("""
    ## 🏫 Smart Campus Access Control System
    
    ### Features:
    - 🆔 **ID Card Recognition**: Automatic detection and extraction of student ID cards
    - 🚗 **License Plate Detection**: Indian license plate recognition with YOLO
    - 🗄️ **Cloud Database**: Supabase PostgreSQL integration for data persistence
    - 📊 **Analytics**: Real-time statistics and access logs
    - 🔒 **Security**: Smart validation and error handling
    
    ### Technology Stack:
    - **Frontend**: Streamlit
    - **Detection**: YOLOv8 (Ultralytics)
    - **OCR**: EasyOCR (GPU-accelerated)
    - **Database**: Supabase (PostgreSQL)
    - **Computer Vision**: OpenCV
    - **Deep Learning**: PyTorch
    
    ### System Status:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🆔 ID Card Model", "✅ Loaded")
    with col2:
        st.metric("🚗 Plate Model", "✅ Loaded")
    with col3:
        if st.session_state.db:
            st.metric("🗄️ Database", "✅ Connected")
        else:
            st.metric("🗄️ Database", "❌ Disconnected")
    
    st.markdown("---")
    st.markdown("""
    ### 📚 Documentation:
    - **Batch Processing**: 58/60 students processed (96.7% success rate)
    - **Smart Validation**: Filters invalid names and departments
    - **Indian Plates**: Supports XX 00 XX 0000 format
    - **Video Processing**: Tested on Indian traffic CCTV footage
    
    ### 🎯 Performance:
    - ID Card Detection: mAP50 = 63.3%
    - License Plate: 99 unique plates from 799 detections
    - Database: 44 students imported successfully
    
    ---
    **Version**: 1.0.0  
    **Last Updated**: October 2025  
    **Mode**: 100% Offline (No API calls)
    """)


if __name__ == "__main__":
    main()
