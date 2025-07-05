#!/usr/bin/env python3
"""
AI Coding Assistant Launcher
Simple launcher script for the educational AI coding assistant demo.
"""

import sys
import os
import json

def check_requirements():
    """Check if required packages are installed."""
    try:
        import openai
        print("✓ OpenAI package found")
    except ImportError:
        print("✗ OpenAI package not found. Please install it with:")
        print("  pip install openai")
        return False
    
    try:
        import tkinter
        print("✓ Tkinter found")
    except ImportError:
        print("✗ Tkinter not found. Please install tkinter:")
        print("  On Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  On macOS: should be included with Python")
        print("  On Windows: should be included with Python")
        return False
    
    return True

def check_config():
    """Check if configuration file exists and is valid."""
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        print(f"✗ Configuration file '{config_file}' not found")
        print("Please create config.json with your OpenAI API key")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        api_key = config.get('openai_api_key', '')
        if not api_key or api_key == "your-openai-api-key-here":
            print("✗ OpenAI API key not configured")
            print("Please edit config.json and add your OpenAI API key")
            return False
        
        print("✓ Configuration file valid")
        return True
        
    except json.JSONDecodeError:
        print("✗ Configuration file contains invalid JSON")
        return False
    except Exception as e:
        print(f"✗ Error reading configuration: {e}")
        return False

def main():
    """Main launcher function."""
    print("AI Coding Assistant - Educational Demo")
    print("=" * 40)
    
    # Check requirements
    print("\nChecking requirements...")
    if not check_requirements():
        print("\nPlease install missing requirements and try again.")
        sys.exit(1)
    
    # Check configuration
    print("\nChecking configuration...")
    if not check_config():
        print("\nPlease fix configuration issues and try again.")
        sys.exit(1)
    
    # All checks passed, launch the application
    print("\n✓ All checks passed! Launching AI Coding Assistant...")
    print("\nInstructions:")
    print("• Type Python code to get AI completions")
    print("• Ghost text appears as gray, italic suggestions")
    print("• Press Tab to accept completions")
    print("• Continue typing to dismiss suggestions")
    print("\nEnjoy coding with AI assistance!")
    print("=" * 40)
    
    try:
        from code_editor import main as editor_main
        editor_main()
    except KeyboardInterrupt:
        print("\n\nApplication closed by user.")
    except Exception as e:
        print(f"\nError launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
