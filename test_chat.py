"""
Test script to verify chat request/response functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_completion_engine import AICompletionEngine

def test_chat_display():
    """Test that chat request/response capture works correctly."""
    print("Testing Chat Request/Response Capture...")
    print("=" * 50)
    
    try:
        # Initialize the engine
        engine = AICompletionEngine()
        print("✓ AI Engine initialized successfully")
        
        # Test completion request
        context_before = "def calculate_area(width, height):"
        cursor_line = "    return width *"
        context_after = ""
        
        print(f"\nTesting with:")
        print(f"Context before: '{context_before}'")
        print(f"Cursor line: '{cursor_line}'")
        print(f"Context after: '{context_after}'")
        
        # Get completion
        completion = engine.get_completion(context_before, cursor_line, context_after)
        print(f"\nCompletion result: '{completion}'")
        
        # Get chat info
        request, response = engine.get_last_chat_info()
        
        print(f"\n--- CHAT REQUEST (length: {len(request) if request else 0}) ---")
        if request:
            print(request)
        else:
            print("NO REQUEST CAPTURED!")
            
        print(f"\n--- CHAT RESPONSE ---")
        if response:
            print(response)
        else:
            print("NO RESPONSE CAPTURED!")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_display()
