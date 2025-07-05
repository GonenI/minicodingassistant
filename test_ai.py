"""
Simple test script to debug the AI completion engine
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_completion_engine import AICompletionEngine

def test_ai_engine():
    """Test the AI completion engine with debug output."""
    print("Testing AI Completion Engine...")
    print("=" * 50)
    
    try:
        # Initialize the engine
        engine = AICompletionEngine()
        print("✓ AI Engine initialized successfully")
        
        # Test simple completion
        print("\nTesting completion...")
        context_before = "def calculate_sum(a, b):"
        cursor_line = "    return a +"
        context_after = ""
        
        print(f"Context before: '{context_before}'")
        print(f"Cursor line: '{cursor_line}'")
        print(f"Context after: '{context_after}'")
        
        completion = engine.get_completion(context_before, cursor_line, context_after)
        
        if completion:
            print(f"✓ Got completion: '{completion}'")
        else:
            print("✗ No completion received")
            
        # Show stats
        stats = engine.get_stats()
        print(f"\nEngine stats: {stats}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_engine()
