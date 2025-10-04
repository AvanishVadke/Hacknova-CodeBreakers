"""
Quick Viewer for Batch ID Card Processing Results
View the JSON results in an organized, readable format
"""

import json
from pathlib import Path

def view_results(json_path):
    """Display batch processing results"""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print("=" * 80)
    print(f"📊 BATCH PROCESSING RESULTS - {len(results)} Images")
    print("=" * 80)
    
    # Statistics
    successful = sum(1 for r in results if r.get('success'))
    with_id = sum(1 for r in results if r.get('moodle_id'))
    with_name = sum(1 for r in results if r.get('name'))
    with_dept = sum(1 for r in results if r.get('department'))
    
    print(f"\n✅ Successful: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print(f"🆔 Moodle ID Found: {with_id}/{len(results)} ({with_id/len(results)*100:.1f}%)")
    print(f"👤 Name Found: {with_name}/{len(results)} ({with_name/len(results)*100:.1f}%)")
    print(f"🏢 Department Found: {with_dept}/{len(results)} ({with_dept/len(results)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("📋 DETAILED RESULTS")
    print("=" * 80)
    
    for idx, result in enumerate(results, 1):
        print(f"\n[{idx}] {result['filename']}")
        print("-" * 80)
        
        if result.get('success'):
            if result.get('moodle_id'):
                conf = result.get('confidence_scores', {}).get('moodle_id', 0)
                print(f"  🆔 Moodle ID: {result['moodle_id']} (confidence: {conf:.2f})")
            
            if result.get('name'):
                conf = result.get('confidence_scores', {}).get('name', 0)
                print(f"  👤 Name: {result['name']} (confidence: {conf:.2f})")
            
            if result.get('department'):
                conf = result.get('confidence_scores', {}).get('department', 0)
                print(f"  🏢 Department: {result['department']} (confidence: {conf:.2f})")
            
            if result.get('card_detected'):
                bbox = result.get('card_bbox', {})
                print(f"  📦 Card Detected: [{bbox.get('x')}, {bbox.get('y')}, {bbox.get('width')}, {bbox.get('height')}]")
            
            # Show all OCR text found
            if result.get('all_text_found'):
                print(f"  📝 All Text Found ({len(result['all_text_found'])} items):")
                for text_item in result['all_text_found'][:5]:  # Show first 5
                    print(f"     - '{text_item['text']}' (conf: {text_item['confidence']:.2f})")
                if len(result['all_text_found']) > 5:
                    print(f"     ... and {len(result['all_text_found']) - 5} more")
        else:
            print(f"  ⚠️  Failed to extract data")
            if 'error' in result:
                print(f"     Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print("✅ View Complete")
    print("=" * 80)


def view_summary(json_path):
    """Display summary statistics only"""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY STATISTICS")
    print("=" * 80)
    
    # Group by success status
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    print(f"\n✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    # Field statistics
    print(f"\n📊 Field Extraction:")
    print(f"  🆔 Moodle ID: {sum(1 for r in results if r.get('moodle_id'))}/{len(results)}")
    print(f"  👤 Name: {sum(1 for r in results if r.get('name'))}/{len(results)}")
    print(f"  🏢 Department: {sum(1 for r in results if r.get('department'))}/{len(results)}")
    
    # Complete records (all 3 fields)
    complete = [r for r in results if r.get('moodle_id') and r.get('name') and r.get('department')]
    print(f"\n🎯 Complete Records (ID + Name + Dept): {len(complete)}/{len(results)}")
    
    # Confidence averages
    id_confs = [r['confidence_scores']['moodle_id'] for r in results if r.get('confidence_scores', {}).get('moodle_id')]
    name_confs = [r['confidence_scores']['name'] for r in results if r.get('confidence_scores', {}).get('name')]
    dept_confs = [r['confidence_scores']['department'] for r in results if r.get('confidence_scores', {}).get('department')]
    
    if id_confs:
        print(f"\n📈 Average Confidence:")
        print(f"  🆔 Moodle ID: {sum(id_confs)/len(id_confs):.2%}")
    if name_confs:
        print(f"  👤 Name: {sum(name_confs)/len(name_confs):.2%}")
    if dept_confs:
        print(f"  🏢 Department: {sum(dept_confs)/len(dept_confs):.2%}")
    
    # Show complete records
    if complete:
        print(f"\n✨ Complete Records:")
        for r in complete:
            print(f"  • {r['filename']}: {r['moodle_id']} - {r['name']} - {r['department']}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='View Batch ID Card Processing Results')
    parser.add_argument('--json', type=str, default='outputs/id_card_data/batch_results.json',
                       help='JSON results file (default: outputs/id_card_data/batch_results.json)')
    parser.add_argument('--summary', action='store_true',
                       help='Show summary only')
    
    args = parser.parse_args()
    
    json_path = Path(args.json)
    
    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        return
    
    if args.summary:
        view_summary(json_path)
    else:
        view_results(json_path)


if __name__ == "__main__":
    main()
