"""
AI Code Completion Engine
Handles communication with OpenAI API for code completion suggestions.
"""

import json
import time
from typing import Optional, Dict, Any
import openai
from openai import OpenAI


class AICompletionEngine:
    """
    Manages AI-powered code completion using OpenAI's API.
    
    This class implements several best practices from tools like GitHub Copilot:
    - Debouncing to avoid excessive API calls
    - Context-aware prompting with surrounding code
    - Caching to improve performance
    - Smart prompt engineering for better completions
    """
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the AI completion engine with configuration."""
        self.config = self._load_config(config_path)
        self.client: Optional[OpenAI] = None
        self._last_request_time = 0
        self._completion_cache = {}  # Simple cache for recent completions
        self._setup_openai_client()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Configuration file {config_path} not found. Please create it with your OpenAI API key.")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in configuration file {config_path}")
    
    def _setup_openai_client(self):
        """Initialize OpenAI client with API key."""
        print(f"[DEBUG] AI Engine: Setting up OpenAI client...")
        api_key = self.config.get('openai_api_key')
        if not api_key or api_key == "your-openai-api-key-here":
            print(f"[DEBUG] AI Engine: Invalid API key")
            raise Exception("Please set your OpenAI API key in config.json")
        
        print(f"[DEBUG] AI Engine: API key found, length: {len(api_key)}")
        self.client = OpenAI(api_key=api_key)
        print(f"[DEBUG] AI Engine: OpenAI client created successfully")
    
    def _should_debounce(self) -> bool:
        """
        Check if we should debounce this request to avoid too frequent API calls.
        This is a key optimization used by modern coding assistants.
        """
        current_time = time.time() * 1000  # Convert to milliseconds
        delay_ms = self.config.get('completion_delay_ms', 500)
        
        if current_time - self._last_request_time < delay_ms:
            return True
        
        self._last_request_time = current_time
        return False
    
    def _create_cache_key(self, context_before: str, context_after: str, cursor_line: str) -> str:
        """
        Create a cache key for the completion request.
        
        This is a simple implementation for educational purposes.
        Real coding assistants use more sophisticated semantic caching.
        
        Current strategy: Cache based on immediate context patterns
        - This will rarely hit but demonstrates the concept
        - Better strategies would use AST analysis, token patterns, etc.
        """
        # Simple hash-like key based on context
        combined = f"{context_before[-100:]}{cursor_line}{context_after[:50:]}"
        cache_key = combined.replace(' ', '').replace('\n', '')
        
        # Add comment about cache effectiveness
        print(f"[DEBUG] Cache: Key created from {len(context_before)} chars before, "
              f"'{cursor_line}' current, {len(context_after)} chars after")
        
        return cache_key
    
    def _build_completion_prompt(self, context_before: str, cursor_line: str, context_after: str) -> str:
        """
        Build an effective prompt for code completion.
        This follows patterns used by successful AI coding assistants.
        """
        prompt = f"""You are an AI coding assistant. Complete the Python code at the cursor position.

Context before:
{context_before}

Current line (cursor at end): {cursor_line}

Context after:
{context_after}

Complete the code at the cursor position. Provide only the completion text, no explanations.
Focus on:
1. Syntactically correct Python code
2. Following the existing code style and patterns
3. Completing the current statement or adding the next logical statement
4. Keeping the completion concise and relevant

Completion:"""
        
        return prompt
    
    def get_completion(self, context_before: str, cursor_line: str, context_after: str) -> Optional[str]:
        """
        Get AI code completion for the given context.
        
        Args:
            context_before: Code lines before the cursor
            cursor_line: The current line where cursor is positioned
            context_after: Code lines after the cursor
            
        Returns:
            Completion suggestion or None if no suggestion available
        """
        print(f"[DEBUG] AI Engine: get_completion called")
        print(f"[DEBUG] Context before: '{context_before[-50:]}'")  # Last 50 chars
        print(f"[DEBUG] Cursor line: '{cursor_line}'")
        print(f"[DEBUG] Context after: '{context_after[:50]}'")  # First 50 chars
        
        # Store the last request for display purposes
        self.last_request_prompt = None
        self.last_response = None
        
        # Implement debouncing to avoid excessive API calls
        if self._should_debounce():
            print(f"[DEBUG] AI Engine: Request debounced")
            return None
        
        # Check cache first
        cache_key = self._create_cache_key(context_before, context_after, cursor_line)
        print(f"[DEBUG] AI Engine: Cache key: {cache_key[:30]}...")
        if cache_key in self._completion_cache:
            print(f"[DEBUG] AI Engine: Cache hit!")
            return self._completion_cache[cache_key]
        
        print(f"[DEBUG] AI Engine: Making API request...")
        try:
            # Build the prompt
            prompt = self._build_completion_prompt(context_before, cursor_line, context_after)
            print(f"[DEBUG] AI Engine: Prompt length: {len(prompt)} chars")
            print(f"[DEBUG] AI Engine: Full prompt: {prompt[:200]}...")  # Show first 200 chars for debugging
            
            # Store prompt for display
            self.last_request_prompt = prompt
            
            # Ensure client is initialized
            if not self.client:
                print(f"[DEBUG] AI Engine: ERROR - Client not initialized!")
                return None
            
            # Make API request
            print(f"[DEBUG] AI Engine: Sending request to OpenAI...")
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are a helpful Python code completion assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.get('max_tokens', 100),
                temperature=self.config.get('temperature', 0.3),
                stop=["\n\n", "```"]  # Stop at double newline or code block end
            )
            print(f"[DEBUG] AI Engine: Got response from OpenAI")
            
            # Safely extract completion
            if response.choices and response.choices[0].message.content:
                completion = response.choices[0].message.content.strip()
                print(f"[DEBUG] AI Engine: Completion: '{completion}'")
                
                # Store response for display
                self.last_response = completion
            else:
                print(f"[DEBUG] AI Engine: No completion in response")
                self.last_response = "No completion received"
                return None
            
            # Cache the result
            self._completion_cache[cache_key] = completion
            print(f"[DEBUG] AI Engine: Cached completion")
            
            # Keep cache size reasonable
            if len(self._completion_cache) > 50:
                # Remove oldest entries (simple FIFO)
                oldest_key = next(iter(self._completion_cache))
                del self._completion_cache[oldest_key]
                print(f"[DEBUG] AI Engine: Cache cleanup, removed oldest entry")
            
            return completion
            
        except Exception as e:
            print(f"[DEBUG] AI Engine: ERROR - {e}")
            print(f"Error getting AI completion: {e}")
            # Store error for display
            self.last_response = f"ERROR: {str(e)}"
            return None
    
    def get_last_chat_info(self) -> tuple[Optional[str], Optional[str]]:
        """Get the last request prompt and response for display."""
        request = getattr(self, 'last_request_prompt', None)
        response = getattr(self, 'last_response', None)
        print(f"[DEBUG] AI Engine: get_last_chat_info - Request exists: {request is not None}")
        print(f"[DEBUG] AI Engine: get_last_chat_info - Response: '{response}'")
        if request:
            print(f"[DEBUG] AI Engine: Request preview: {request[:100]}...")
        return request, response
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about API usage and caching."""
        return {
            "cache_size": len(self._completion_cache),
            "model": self.config.get('model', 'gpt-3.5-turbo'),
            "max_tokens": self.config.get('max_tokens', 100),
            "completion_delay_ms": self.config.get('completion_delay_ms', 500)
        }
