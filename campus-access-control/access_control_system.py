"""
Unified Campus Access Control System
Integrates vehicle plate recognition and ID card verification
Makes access decisions based on both inputs
"""

import cv2
import json
import threading
import queue
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add modules to path
sys.path.append(str(Path(__file__).resolve().parent))
from vehicle_plate_recognizer import VehiclePlateRecognizer

# Use OFFLINE ID card recognition (no API calls, 100% local)
try:
    from offline_id_card_recognizer import OfflineIDCardRecognizer as IDCardVerifier
    print("✅ Using Offline ID Card Recognizer (100% Local, No API)")
except Exception as e:
    print(f"⚠️  Offline recognizer not available: {e}")
    print("   Falling back to basic verifier...")
    from id_card_verifier import IDCardVerifier

from config.config import *


class AccessControlSystem:
    """
    Unified access control system for campus entry/exit
    """
    
    def __init__(self, vehicle_model_path=None, id_card_model_path=None):
        """
        Initialize the unified access control system
        
        Args:
            vehicle_model_path (str): Path to vehicle detection model
            id_card_model_path (str): Path to ID card detection model
        """
        print("=" * 70)
        print("🏛️  SMART CAMPUS ACCESS VERIFICATION SYSTEM")
        print("=" * 70)
        print("🚀 Initializing modules...")
        
        # Initialize recognizers
        print("\n[1/2] Initializing Vehicle Plate Recognizer...")
        self.vehicle_recognizer = VehiclePlateRecognizer(
            model_path=vehicle_model_path,
            use_gpu=USE_GPU
        )
        
        print("\n[2/2] Initializing ID Card Verifier...")
        self.id_card_verifier = IDCardVerifier(
            model_path=id_card_model_path,
            use_gpu=USE_GPU
        )
        
        # Access records
        self.pending_verifications = {}  # Temporary storage for partial verifications
        self.access_log = []
        
        # Queues for multi-threaded processing
        self.vehicle_queue = queue.Queue()
        self.id_card_queue = queue.Queue()
        
        # Statistics
        self.stats = {
            'total_attempts': 0,
            'access_granted': 0,
            'access_denied': 0,
            'vehicle_only': 0,
            'id_card_only': 0,
            'both_verified': 0
        }
        
        print("\n✅ System initialized successfully!")
        print("=" * 70)
    
    def match_vehicle_and_id(self, vehicle_data, id_card_data):
        """
        Match vehicle and ID card data for verification
        
        Args:
            vehicle_data (dict): Vehicle plate data
            id_card_data (dict): ID card data
            
        Returns:
            dict: Matching result
        """
        match_result = {
            'timestamp': get_timestamp(),
            'vehicle': vehicle_data,
            'id_card': id_card_data,
            'match_status': 'pending',
            'access_decision': 'pending'
        }
        
        # Check if both have valid data
        vehicle_valid = vehicle_data and vehicle_data.get('is_valid', False)
        id_card_valid = id_card_data and id_card_data.get('is_valid', False)
        
        if REQUIRE_BOTH_VERIFICATIONS:
            # Both must be valid
            if vehicle_valid and id_card_valid:
                match_result['match_status'] = 'matched'
                match_result['access_decision'] = 'granted'
                self.stats['both_verified'] += 1
                self.stats['access_granted'] += 1
            else:
                match_result['match_status'] = 'incomplete'
                match_result['access_decision'] = 'denied'
                match_result['reason'] = 'Both vehicle and ID card required'
                self.stats['access_denied'] += 1
        else:
            # Either one is sufficient
            if vehicle_valid or id_card_valid:
                match_result['match_status'] = 'partial'
                match_result['access_decision'] = 'granted'
                self.stats['access_granted'] += 1
                
                if vehicle_valid and not id_card_valid:
                    self.stats['vehicle_only'] += 1
                elif id_card_valid and not vehicle_valid:
                    self.stats['id_card_only'] += 1
            else:
                match_result['match_status'] = 'failed'
                match_result['access_decision'] = 'denied'
                match_result['reason'] = 'No valid identification'
                self.stats['access_denied'] += 1
        
        self.stats['total_attempts'] += 1
        return match_result
    
    def check_pending_verification(self, moodle_id=None, plate_number=None):
        """
        Check if there's a pending verification waiting to be matched
        
        Args:
            moodle_id (str): Moodle ID to check
            plate_number (str): Vehicle plate to check
            
        Returns:
            dict: Matched verification if found, None otherwise
        """
        current_time = datetime.now()
        
        # Check pending verifications
        for key, pending in list(self.pending_verifications.items()):
            # Check if within time window
            pending_time = datetime.fromisoformat(pending['timestamp'])
            if (current_time - pending_time).seconds > ACCESS_TIME_WINDOW:
                # Expired, remove and deny
                expired = self.pending_verifications.pop(key)
                expired['access_decision'] = 'denied'
                expired['reason'] = 'Verification timeout'
                self.save_access_log(expired)
                continue
            
            # Try to match
            if moodle_id and pending.get('id_card', {}).get('moodle_id') == moodle_id:
                return self.pending_verifications.pop(key)
            
            if plate_number and pending.get('vehicle', {}).get('plate_text') == plate_number:
                return self.pending_verifications.pop(key)
        
        return None
    
    def process_vehicle_detection(self, vehicle_data):
        """
        Process vehicle detection and check for matching ID card
        
        Args:
            vehicle_data (dict): Vehicle detection data
        """
        if not vehicle_data or not vehicle_data.get('is_valid'):
            return
        
        plate_number = vehicle_data.get('plate_text')
        
        # Check for pending ID card verification
        pending = self.check_pending_verification(plate_number=plate_number)
        
        if pending:
            # Found matching ID card
            pending['vehicle'] = vehicle_data
            result = self.match_vehicle_and_id(vehicle_data, pending.get('id_card'))
            self.save_access_log(result)
            print(f"\n✅ ACCESS GRANTED: {pending.get('id_card', {}).get('name')} | Vehicle: {plate_number}")
        else:
            # Store as pending
            pending_key = f"vehicle_{plate_number}_{get_timestamp()}"
            self.pending_verifications[pending_key] = {
                'timestamp': get_timestamp(),
                'vehicle': vehicle_data,
                'id_card': None
            }
            print(f"\n⏳ Vehicle detected: {plate_number} (waiting for ID card)")
    
    def process_id_card_detection(self, id_card_data):
        """
        Process ID card detection and check for matching vehicle
        
        Args:
            id_card_data (dict): ID card detection data
        """
        if not id_card_data or not id_card_data.get('is_valid'):
            return
        
        moodle_id = id_card_data.get('moodle_id')
        name = id_card_data.get('name')
        
        # Check for pending vehicle verification
        pending = self.check_pending_verification(moodle_id=moodle_id)
        
        if pending:
            # Found matching vehicle
            pending['id_card'] = id_card_data
            result = self.match_vehicle_and_id(pending.get('vehicle'), id_card_data)
            self.save_access_log(result)
            print(f"\n✅ ACCESS GRANTED: {name} (ID: {moodle_id}) | Vehicle: {pending.get('vehicle', {}).get('plate_text')}")
        else:
            # Store as pending
            pending_key = f"id_card_{moodle_id}_{get_timestamp()}"
            self.pending_verifications[pending_key] = {
                'timestamp': get_timestamp(),
                'vehicle': None,
                'id_card': id_card_data
            }
            print(f"\n⏳ ID Card detected: {name} (ID: {moodle_id}) (waiting for vehicle)")
    
    def save_access_log(self, access_record):
        """
        Save access decision to log
        
        Args:
            access_record (dict): Access decision record
        """
        self.access_log.append(access_record)
        
        # Save to file
        log_filename = f"access_log_{get_date_string()}.json"
        log_path = ACCESS_LOG_DIR / log_filename
        
        # Load existing log if exists
        if log_path.exists():
            with open(log_path, 'r', encoding='utf-8') as f:
                existing_log = json.load(f)
        else:
            existing_log = {'date': get_date_string(), 'records': []}
        
        # Append new record
        existing_log['records'].append(access_record)
        
        # Save
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(existing_log, f, indent=2, ensure_ascii=False)
        
        # Alert if access denied
        if SEND_ALERTS and access_record['access_decision'] == 'denied':
            self.send_alert(access_record)
    
    def send_alert(self, access_record):
        """
        Send alert for unauthorized access attempt
        
        Args:
            access_record (dict): Access record
        """
        alert_msg = f"🚨 ALERT: Access Denied at {access_record['timestamp']}"
        
        if access_record.get('id_card'):
            alert_msg += f"\n   ID: {access_record['id_card'].get('moodle_id')} - {access_record['id_card'].get('name')}"
        
        if access_record.get('vehicle'):
            alert_msg += f"\n   Vehicle: {access_record['vehicle'].get('plate_text')}"
        
        alert_msg += f"\n   Reason: {access_record.get('reason', 'Verification failed')}"
        
        print(alert_msg)
        
        # Save alert to file
        alert_path = ACCESS_LOG_DIR / f"alerts_{get_date_string()}.txt"
        with open(alert_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{alert_msg}\n")
            f.write("-" * 70 + "\n")
    
    def run_dual_camera_system(self, vehicle_camera_index=0, id_card_camera_index=1, duration=None):
        """
        Run system with two cameras (one for vehicles, one for ID cards)
        
        Args:
            vehicle_camera_index (int): Camera index for vehicle detection
            id_card_camera_index (int): Camera index for ID card detection
            duration (int): Duration in seconds (None = infinite)
        """
        print("\n🎥 Starting dual camera system...")
        print(f"   Camera {vehicle_camera_index}: Vehicle Detection")
        print(f"   Camera {id_card_camera_index}: ID Card Verification")
        print("\nPress 'q' to quit")
        
        # Open both cameras
        vehicle_cap = cv2.VideoCapture(vehicle_camera_index)
        id_card_cap = cv2.VideoCapture(id_card_camera_index)
        
        if not vehicle_cap.isOpened() or not id_card_cap.isOpened():
            print("❌ Failed to open one or both cameras")
            return
        
        # Set camera properties
        for cap in [vehicle_cap, id_card_cap]:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        
        frame_count = 0
        start_time = datetime.now()
        
        while True:
            # Read frames
            ret1, vehicle_frame = vehicle_cap.read()
            ret2, id_card_frame = id_card_cap.read()
            
            if not ret1 or not ret2:
                print("❌ Failed to read from cameras")
                break
            
            frame_count += 1
            timestamp = get_timestamp()
            
            # Process vehicle frame
            vehicle_results, vehicle_annotated = self.vehicle_recognizer.detect_and_extract(
                vehicle_frame, frame_count, timestamp
            )
            
            # Process ID card frame
            id_card_results, id_card_annotated = self.id_card_verifier.detect_and_extract_id_card(
                id_card_frame, frame_count, timestamp
            )
            
            # Process detections
            if vehicle_results['detections']:
                for detection in vehicle_results['detections']:
                    self.process_vehicle_detection(detection)
            
            if id_card_results['id_cards']:
                for card in id_card_results['id_cards']:
                    self.process_id_card_detection(card)
            
            # Display both feeds
            combined = np.hstack([vehicle_annotated, id_card_annotated])
            cv2.imshow('Campus Access Control System', combined)
            
            # Display stats
            if frame_count % 30 == 0:
                self.print_stats()
            
            # Handle key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Check duration
            if duration and (datetime.now() - start_time).total_seconds() > duration:
                break
        
        # Cleanup
        vehicle_cap.release()
        id_card_cap.release()
        cv2.destroyAllWindows()
        
        # Final report
        self.generate_session_report()
    
    def run_single_camera_system(self, camera_index=0, duration=None):
        """
        Run system with single camera (alternating between vehicle and ID card detection)
        
        Args:
            camera_index (int): Camera index
            duration (int): Duration in seconds (None = infinite)
        """
        print("\n📷 Starting single camera system...")
        print("   Press '1' for Vehicle Mode")
        print("   Press '2' for ID Card Mode")
        print("   Press 'q' to quit")
        
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("❌ Failed to open camera")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        
        mode = 'vehicle'  # Start with vehicle mode
        frame_count = 0
        start_time = datetime.now()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            timestamp = get_timestamp()
            
            # Process based on mode
            if mode == 'vehicle':
                results, annotated = self.vehicle_recognizer.detect_and_extract(
                    frame, frame_count, timestamp
                )
                
                if results['detections']:
                    for detection in results['detections']:
                        self.process_vehicle_detection(detection)
                
                # Add mode label
                cv2.putText(annotated, "MODE: VEHICLE DETECTION", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            else:  # ID card mode
                results, annotated = self.id_card_verifier.detect_and_extract_id_card(
                    frame, frame_count, timestamp
                )
                
                if results['id_cards']:
                    for card in results['id_cards']:
                        self.process_id_card_detection(card)
                
                # Add mode label
                cv2.putText(annotated, "MODE: ID CARD VERIFICATION", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display
            cv2.imshow('Campus Access Control System', annotated)
            
            # Handle key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('1'):
                mode = 'vehicle'
                print("\n🚗 Switched to Vehicle Detection Mode")
            elif key == ord('2'):
                mode = 'id_card'
                print("\n🎴 Switched to ID Card Verification Mode")
            
            # Check duration
            if duration and (datetime.now() - start_time).total_seconds() > duration:
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        self.generate_session_report()
    
    def print_stats(self):
        """Print current statistics"""
        print("\n" + "=" * 70)
        print("📊 SYSTEM STATISTICS")
        print("=" * 70)
        print(f"Total Attempts:      {self.stats['total_attempts']}")
        print(f"Access Granted:      {self.stats['access_granted']} ✅")
        print(f"Access Denied:       {self.stats['access_denied']} ❌")
        print(f"Both Verified:       {self.stats['both_verified']}")
        print(f"Vehicle Only:        {self.stats['vehicle_only']}")
        print(f"ID Card Only:        {self.stats['id_card_only']}")
        print(f"Pending:             {len(self.pending_verifications)}")
        print("=" * 70)
    
    def generate_session_report(self):
        """Generate final session report"""
        print("\n" + "=" * 70)
        print("📄 SESSION REPORT")
        print("=" * 70)
        
        self.print_stats()
        
        # Save report
        report = {
            'session_ended': get_timestamp(),
            'statistics': self.stats,
            'pending_verifications': len(self.pending_verifications),
            'total_access_logs': len(self.access_log)
        }
        
        report_path = ACCESS_LOG_DIR / get_output_filename('session_report')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Report saved to: {report_path}")
        print("=" * 70)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Campus Access Control System')
    parser.add_argument('--mode', choices=['single', 'dual'], default='single',
                       help='Camera mode: single or dual')
    parser.add_argument('--vehicle-camera', type=int, default=0,
                       help='Vehicle camera index')
    parser.add_argument('--id-card-camera', type=int, default=1,
                       help='ID card camera index (dual mode only)')
    parser.add_argument('--duration', type=int, help='Duration in seconds')
    
    args = parser.parse_args()
    
    # Initialize system
    system = AccessControlSystem()
    
    # Run system
    if args.mode == 'dual':
        system.run_dual_camera_system(
            vehicle_camera_index=args.vehicle_camera,
            id_card_camera_index=args.id_card_camera,
            duration=args.duration
        )
    else:
        system.run_single_camera_system(
            camera_index=args.vehicle_camera,
            duration=args.duration
        )


if __name__ == "__main__":
    main()
