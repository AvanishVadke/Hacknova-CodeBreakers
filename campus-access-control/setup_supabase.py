"""
Quick Supabase Setup and Test Script
Guides user through connection setup and imports batch results
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).resolve().parent))


def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found!")
        print("\n📋 Please create .env file:")
        print("   1. Copy .env.example to .env")
        print("   2. Fill in your Supabase credentials")
        print("\n💡 Get credentials from: https://supabase.com/dashboard")
        print("   → Settings → Database → Connection String\n")
        return False
    
    # Check if variables are set
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['SUPABASE_HOST', 'SUPABASE_USER', 'SUPABASE_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\n📋 Please update .env file with these variables\n")
        return False
    
    print("✅ .env file configured correctly")
    return True


def test_connection():
    """Test Supabase connection"""
    print("\n🔌 Testing Supabase connection...")
    
    try:
        from database.supabase_manager import SupabaseManager
        
        db = SupabaseManager()
        
        if db.connect():
            print("✅ Connected to Supabase successfully!")
            
            # Create tables
            print("\n📦 Creating database tables...")
            db.create_tables()
            print("✅ Tables created successfully!")
            
            # Test operations
            print("\n🧪 Testing database operations...")
            
            # Test student insert
            db.insert_student(
                moodle_id='20230001',
                name='Test Student',
                department='COMPUTER ENGINEERING'
            )
            print("✅ Inserted test student")
            
            # Test ID card log
            db.log_id_card_access(
                moodle_id='20230001',
                name='Test Student',
                department='COMPUTER ENGINEERING',
                confidence=0.95,
                camera_id='test_camera',
                status='allowed'
            )
            print("✅ Logged test ID card access")
            
            # Test vehicle insert
            db.insert_vehicle(license_plate='KA 02 HN 1828')
            print("✅ Inserted test vehicle")
            
            # Test vehicle log
            db.log_vehicle_access(
                license_plate='KA 02 HN 1828',
                confidence=0.90,
                camera_id='test_camera',
                status='allowed'
            )
            print("✅ Logged test vehicle access")
            
            # Get statistics
            print("\n📊 Database Statistics:")
            stats = db.get_today_statistics()
            if stats:
                print(f"   🆔 ID Card Entries: {stats['id_card_entries']}")
                print(f"   🚗 Vehicle Entries: {stats['vehicle_entries']}")
                print(f"   📈 Total Entries: {stats['total_entries']}")
            
            db.disconnect()
            
            print("\n✅ All tests passed!")
            return True
            
        else:
            print("❌ Failed to connect to Supabase")
            print("   Check your credentials in .env file")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def import_batch_results():
    """Import batch processing results"""
    print("\n📥 Importing Batch Results...")
    
    # Find batch results file
    batch_files = [
        'outputs/id_card_data/batch_results_improved.json',
        'outputs/id_card_data/batch_results.json',
        'batch_results_improved.json',
        'batch_results.json'
    ]
    
    batch_file = None
    for file in batch_files:
        if Path(file).exists():
            batch_file = file
            break
    
    if not batch_file:
        print("⚠️  No batch results file found")
        print("   Expected locations:")
        for file in batch_files:
            print(f"   - {file}")
        return False
    
    print(f"📂 Found batch results: {batch_file}")
    
    try:
        from database.supabase_manager import SupabaseManager
        
        db = SupabaseManager()
        
        if db.connect():
            count = db.bulk_import_students_from_json(batch_file)
            print(f"✅ Imported {count} students to database")
            
            db.disconnect()
            return True
        else:
            print("❌ Failed to connect to database")
            return False
            
    except Exception as e:
        print(f"❌ Error importing: {e}")
        return False


def show_menu():
    """Show interactive menu"""
    print("\n" + "=" * 70)
    print("🗄️  SUPABASE SETUP & TEST UTILITY")
    print("=" * 70)
    print("\n📋 Select an option:")
    print("   1. Test Connection & Create Tables")
    print("   2. Import Batch Results (58 students)")
    print("   3. View Today's Statistics")
    print("   4. View Recent Logs")
    print("   5. Run All Setup Steps")
    print("   0. Exit")
    print()
    
    choice = input("Enter choice (0-5): ").strip()
    return choice


def view_statistics():
    """View today's statistics"""
    try:
        from database.supabase_manager import SupabaseManager
        
        db = SupabaseManager()
        
        if db.connect():
            print("\n📊 Today's Statistics:")
            stats = db.get_today_statistics()
            
            if stats:
                print(f"   🆔 ID Card Entries: {stats['id_card_entries']}")
                print(f"   🚗 Vehicle Entries: {stats['vehicle_entries']}")
                print(f"   📈 Total Entries: {stats['total_entries']}")
            else:
                print("   No entries today")
            
            db.disconnect()
        else:
            print("❌ Failed to connect to database")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def view_logs():
    """View recent logs"""
    try:
        from database.supabase_manager import SupabaseManager
        
        db = SupabaseManager()
        
        if db.connect():
            print("\n📋 Recent ID Card Logs:")
            id_logs = db.get_recent_id_card_logs(limit=10)
            
            if id_logs:
                for i, log in enumerate(id_logs, 1):
                    print(f"   {i}. {log['moodle_id']} - {log['name']}")
                    print(f"      Dept: {log['department']}")
                    print(f"      Time: {log['access_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"      Camera: {log['camera_id']}")
                    print()
            else:
                print("   No logs found")
            
            print("\n🚗 Recent Vehicle Logs:")
            vehicle_logs = db.get_recent_vehicle_logs(limit=10)
            
            if vehicle_logs:
                for i, log in enumerate(vehicle_logs, 1):
                    print(f"   {i}. {log['license_plate']}")
                    print(f"      Confidence: {log['confidence']:.2f}")
                    print(f"      Time: {log['access_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"      Camera: {log['camera_id']}")
                    print()
            else:
                print("   No logs found")
            
            db.disconnect()
        else:
            print("❌ Failed to connect to database")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def run_all_setup():
    """Run all setup steps"""
    print("\n🚀 Running Complete Setup...")
    
    if not check_env_file():
        return
    
    if not test_connection():
        return
    
    import_batch_results()
    view_statistics()
    
    print("\n✅ Setup complete!")


def main():
    """Main function"""
    # Check dependencies
    try:
        import psycopg2
        import dotenv
    except ImportError as e:
        print("❌ Missing dependencies!")
        print("\n📦 Please install:")
        print("   pip install python-dotenv psycopg2-binary")
        return
    
    while True:
        choice = show_menu()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        
        elif choice == '1':
            if check_env_file():
                test_connection()
        
        elif choice == '2':
            if check_env_file():
                import_batch_results()
        
        elif choice == '3':
            if check_env_file():
                view_statistics()
        
        elif choice == '4':
            if check_env_file():
                view_logs()
        
        elif choice == '5':
            run_all_setup()
        
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
