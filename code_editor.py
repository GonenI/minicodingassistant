"""
Python Code Editor with AI Completion
A simple but educational Python editor that demonstrates AI code completion techniques.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
import time
from typing import Optional, Tuple
from ai_completion_engine import AICompletionEngine


class CodeEditor:
    """
    A Python code editor with AI-powered completion and ghost text.
    
    This implementation demonstrates key concepts from modern AI coding assistants:
    - Ghost text for completion previews
    - Smart context extraction
    - Non-blocking AI requests
    - Clean, educational code structure
    """
    
    def __init__(self, root: tk.Tk):
        """Initialize the code editor."""
        self.root = root
        self.root.title("AI Python Code Assistant - Educational Demo")
        self.root.geometry("1000x700")
        
        # Initialize AI completion engine
        print(f"[DEBUG] Editor: Initializing AI completion engine...")
        try:
            self.ai_engine = AICompletionEngine()
            print(f"[DEBUG] Editor: AI engine initialized successfully")
        except Exception as e:
            print(f"[DEBUG] Editor: AI engine initialization failed: {e}")
            messagebox.showerror("Configuration Error", str(e))
            self.ai_engine = None
        
        # Editor state
        self.current_completion = ""
        self.ghost_text_start_pos = None
        self.completion_thread = None
        self.last_completion_request = 0
        
        # Chat display state
        self.chat_color_toggle = False  # False = green, True = black
        
        # Create UI
        self._create_ui()
        self._setup_bindings()
        
        # Status
        self.update_status("Ready - Start typing Python code for AI completions!")
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create menu bar
        self._create_menu()
        
        # Create toolbar
        toolbar = tk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(toolbar, text="New", command=self.new_file).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=5)
        
        # Separator
        tk.Frame(toolbar, width=2, bg="gray").pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # AI controls
        tk.Label(toolbar, text="AI Completion:").pack(side=tk.LEFT, padx=5)
        self.ai_enabled_var = tk.BooleanVar(value=True if self.ai_engine else False)
        tk.Checkbutton(toolbar, text="Enabled", variable=self.ai_enabled_var).pack(side=tk.LEFT)
        
        # Chat controls
        tk.Label(toolbar, text="Chat:").pack(side=tk.LEFT, padx=(20, 5))
        tk.Button(toolbar, text="Clear Chat", command=self.clear_chat_windows).pack(side=tk.LEFT, padx=5)
        
        # Create text editor with line numbers
        editor_frame = tk.Frame(main_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers (simplified)
        self.line_numbers = tk.Text(editor_frame, width=4, padx=3, takefocus=0,
                                   border=0, state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main text editor
        self.text_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            insertbackground="blue",
            selectbackground="lightblue",
            undo=True,
            maxundo=50
        )
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Ghost text tag for AI completion preview
        self.text_editor.tag_configure("ghost_text", foreground="gray", font=("Consolas", 11, "italic"))
        
        # Chat display frames (below editor)
        chat_frame = tk.Frame(main_frame)
        chat_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        
        # Left frame - Chat Request
        request_frame = tk.LabelFrame(chat_frame, text="Chat Request", font=("Arial", 10, "bold"))
        request_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.request_text = scrolledtext.ScrolledText(
            request_frame,
            height=12,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state='disabled'
        )
        self.request_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right frame - Chat Response  
        response_frame = tk.LabelFrame(chat_frame, text="Chat Response", font=("Arial", 10, "bold"))
        response_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.response_text = scrolledtext.ScrolledText(
            response_frame,
            height=12,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state='disabled'
        )
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = tk.Label(status_frame, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # AI stats label
        self.ai_stats_label = tk.Label(status_frame, text="", anchor=tk.E)
        self.ai_stats_label.pack(side=tk.RIGHT)
    
    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def _setup_bindings(self):
        """Setup keyboard bindings and events."""
        # File operations
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        
        # AI completion controls
        self.text_editor.bind('<KeyPress>', self.on_key_press)  # Handle key before insertion
        self.text_editor.bind('<KeyRelease>', self.on_text_change)  # Handle after insertion for completion
        self.text_editor.bind('<Button-1>', self.on_click)
        self.text_editor.bind('<Tab>', self.on_tab_key)
        
        # Manual completion trigger for testing
        self.root.bind('<Control-space>', lambda e: self.request_ai_completion())
        
        # Update line numbers
        self.text_editor.bind('<KeyPress>', lambda e: self.root.after_idle(self.update_line_numbers), add='+')
    
    def on_key_press(self, event):
        """Handle key press BEFORE character insertion - clear ghost text for typing."""
        # Define keys that should clear ghost text (actual content-changing keys)
        content_changing_keys = {
            # Regular printable characters (will have keysym length 1)
            # Special content keys
            'Return', 'BackSpace', 'Delete', 'space'
        }
        
        # Check if this is a content-changing key
        is_content_key = (
            len(event.keysym) == 1 or  # Single character (letters, numbers, symbols)
            event.keysym in content_changing_keys
        )
        
        # Don't clear for navigation and modifier keys, but do clear for arrow keys
        # (since arrow keys should clear ghost text when cursor moves)
        navigation_and_modifier_keys = {
            'Home', 'End', 'Page_Up', 'Page_Down',
            'Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R',
            'Escape', 'Tab', 'Caps_Lock', 'Num_Lock', 'Scroll_Lock',
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'
        }
        
        # Arrow keys should clear ghost text (cursor movement)
        if event.keysym in ['Up', 'Down', 'Left', 'Right']:
            if self.ghost_text_start_pos and self.current_completion:
                print(f"[DEBUG] Editor: Clearing ghost text before cursor movement '{event.keysym}'")
                self.clear_ghost_text()
        elif event.keysym in navigation_and_modifier_keys:
            is_content_key = False
        
        # Clear ghost text before any content-changing key
        if is_content_key and self.ghost_text_start_pos and self.current_completion:
            print(f"[DEBUG] Editor: Clearing ghost text before typing '{event.keysym}'")
            self.clear_ghost_text()
        
        # Allow normal key processing to continue
        return None
    
    def on_text_change(self, event):
        """Handle text changes to trigger AI completion."""
        print(f"[DEBUG] Editor: Text changed, key: {event.keysym}")
        
        # Get current cursor position and text for debugging
        cursor_pos = self.text_editor.index(tk.INSERT)
        current_line = self.text_editor.get(f"{cursor_pos.split('.')[0]}.0", f"{cursor_pos.split('.')[0]}.end")
        print(f"[DEBUG] Editor: Cursor at {cursor_pos}, current line: '{current_line}'")
        
        # Note: Ghost text clearing is now handled in on_key_press before text insertion
        
        # Only request completion for certain keys and if AI is enabled
        if (self.ai_enabled_var.get() and self.ai_engine and 
            event.keysym not in ['Up', 'Down', 'Left', 'Right', 'Tab']):
            
            print(f"[DEBUG] Editor: Conditions met for AI completion request")
            # Use a small delay to avoid too many requests
            self.root.after(300, self.request_ai_completion)
        else:
            reasons = []
            if not self.ai_enabled_var.get():
                reasons.append("AI disabled")
            if not self.ai_engine:
                reasons.append("No AI engine")
            if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Tab']:
                reasons.append(f"Ignored key: {event.keysym}")
            print(f"[DEBUG] Editor: Not requesting completion - {', '.join(reasons)}")
    
    def on_click(self, event):
        """Handle mouse clicks - clear ghost text."""
        self.clear_ghost_text()
    
    def on_tab_key(self, event):
        """Handle Tab key - accept AI completion if available."""
        if self.current_completion and self.ghost_text_start_pos:
            self.accept_completion()
            return "break"  # Prevent default tab behavior
        return None
    
    def clear_ghost_text(self):
        """Clear the ghost text completion preview."""
        if self.ghost_text_start_pos and self.current_completion:
            # Calculate the end position of ghost text
            end_pos = f"{self.ghost_text_start_pos}+{len(self.current_completion)}c"
            
            # Verify that this range still contains our ghost text by checking the tag
            # This prevents accidentally deleting user-typed text
            try:
                # Get the actual text in this range
                actual_text = self.text_editor.get(self.ghost_text_start_pos, end_pos)
                
                # Check if this text has the ghost_text tag
                tags = self.text_editor.tag_names(self.ghost_text_start_pos)
                
                if "ghost_text" in tags and actual_text == self.current_completion:
                    # Safe to delete - this is still our ghost text
                    self.text_editor.delete(self.ghost_text_start_pos, end_pos)
                    print(f"[DEBUG] Editor: Cleared ghost text: '{actual_text}'")
                else:
                    print(f"[DEBUG] Editor: Ghost text range changed, not clearing")
            except tk.TclError:
                # Index might be invalid, just clear our state
                print(f"[DEBUG] Editor: Ghost text position invalid, clearing state only")
            
            # Always clear our state
            self.ghost_text_start_pos = None
            self.current_completion = ""
    
    def accept_completion(self):
        """Accept the current AI completion."""
        if self.current_completion and self.ghost_text_start_pos:
            # Remove ghost text tag and make it regular text
            end_pos = f"{self.ghost_text_start_pos}+{len(self.current_completion)}c"
            self.text_editor.tag_remove("ghost_text", self.ghost_text_start_pos, end_pos)
            
            # Move cursor to end of completion
            self.text_editor.mark_set(tk.INSERT, end_pos)
            
            # Clear completion state
            self.ghost_text_start_pos = None
            self.current_completion = ""
            
            self.update_status("Completion accepted!")
    
    def get_context_around_cursor(self) -> Tuple[str, str, str]:
        """
        Extract context around the cursor for AI completion.
        Returns: (context_before, current_line, context_after)
        """
        cursor_pos = self.text_editor.index(tk.INSERT)
        cursor_line_num = int(cursor_pos.split('.')[0])
        cursor_col_num = int(cursor_pos.split('.')[1])
        
        # Get current line, but exclude ghost text if present
        line_start = f"{cursor_line_num}.0"
        
        # Determine where to end the current line extraction
        if self.ghost_text_start_pos:
            ghost_line_num = int(self.ghost_text_start_pos.split('.')[0])
            ghost_col_num = int(self.ghost_text_start_pos.split('.')[1])
            
            if ghost_line_num == cursor_line_num:
                # Ghost text is on same line, extract only up to ghost text start
                current_line = self.text_editor.get(line_start, self.ghost_text_start_pos)
                print(f"[DEBUG] Context: Excluding ghost text, current line: '{current_line}'")
            else:
                # Ghost text is on different line, extract up to cursor
                current_line = self.text_editor.get(line_start, cursor_pos)
        else:
            # No ghost text, extract up to cursor
            current_line = self.text_editor.get(line_start, cursor_pos)
        
        # Get context before (limited lines)
        lines_before = []
        start_line = max(1, cursor_line_num - 10)  # 10 lines before
        
        for line_num in range(start_line, cursor_line_num):
            line_content = self.text_editor.get(f"{line_num}.0", f"{line_num}.end")
            if line_content.strip():  # Only include non-empty lines
                lines_before.append(line_content)
        
        context_before = '\n'.join(lines_before[-10:])  # Last 10 lines
        
        # Get context after (limited lines)
        lines_after = []
        total_lines = int(self.text_editor.index('end-1c').split('.')[0])
        end_line = min(total_lines, cursor_line_num + 5)  # 5 lines after
        
        for line_num in range(cursor_line_num + 1, end_line + 1):
            line_content = self.text_editor.get(f"{line_num}.0", f"{line_num}.end")
            if line_content.strip():  # Only include non-empty lines
                lines_after.append(line_content)
        
        context_after = '\n'.join(lines_after[:5])  # First 5 lines
        
        return context_before, current_line, context_after
    
    def request_ai_completion(self):
        """Request AI completion in a separate thread to avoid blocking UI."""
        print(f"[DEBUG] Editor: request_ai_completion called")
        
        if not self.ai_engine or not self.ai_enabled_var.get():
            print(f"[DEBUG] Editor: AI not available or disabled")
            return
        
        # Avoid multiple concurrent requests
        current_time = time.time()
        if current_time - self.last_completion_request < 0.5:  # 500ms debounce
            print(f"[DEBUG] Editor: Request debounced (too soon)")
            return
        
        self.last_completion_request = current_time
        
        # Get context
        context_before, current_line, context_after = self.get_context_around_cursor()
        print(f"[DEBUG] Editor: Current line: '{current_line}'")
        print(f"[DEBUG] Editor: Line length: {len(current_line.strip())}")
        
        # Only request completion if we have some content and cursor is at logical end of line
        cursor_pos = self.text_editor.index(tk.INSERT)
        cursor_line_num = int(cursor_pos.split('.')[0])
        cursor_col_num = int(cursor_pos.split('.')[1])
        
        # Get the line end position, but ignore ghost text
        line_start_pos = f"{cursor_line_num}.0"
        line_end_pos = f"{cursor_line_num}.end"
        
        # If we have ghost text, we need to find the logical end (before ghost text)
        logical_line_end_col = cursor_col_num  # Default assumption
        
        if self.ghost_text_start_pos:
            # Ghost text exists, find where it starts on this line
            ghost_line_num = int(self.ghost_text_start_pos.split('.')[0])
            ghost_col_num = int(self.ghost_text_start_pos.split('.')[1])
            
            if ghost_line_num == cursor_line_num:
                # Ghost text is on the same line as cursor
                logical_line_end_col = ghost_col_num
                print(f"[DEBUG] Editor: Ghost text detected at col {ghost_col_num}, using as logical line end")
            else:
                # Ghost text is on a different line, use actual line end
                actual_line_end = self.text_editor.index(line_end_pos)
                logical_line_end_col = int(actual_line_end.split('.')[1])
        else:
            # No ghost text, use actual line end
            actual_line_end = self.text_editor.index(line_end_pos)
            logical_line_end_col = int(actual_line_end.split('.')[1])
        
        print(f"[DEBUG] Editor: Cursor pos: {cursor_pos}")
        print(f"[DEBUG] Editor: Cursor col: {cursor_col_num}, Logical line end col: {logical_line_end_col}")
        
        # More lenient conditions for testing
        if len(current_line.strip()) < 1:  # Minimum line length
            print(f"[DEBUG] Editor: Not requesting - line too short ({len(current_line.strip())} chars)")
            return
        
        # Check if cursor is at or near the logical end of line
        if cursor_col_num < logical_line_end_col - 1:  # Allow cursor to be within 1 char of logical end
            print(f"[DEBUG] Editor: Not requesting - cursor not at logical end of line")
            return
        
        # Start completion in thread
        print(f"[DEBUG] Editor: Starting completion thread...")
        self.completion_thread = threading.Thread(
            target=self._get_completion_async,
            args=(context_before, current_line, context_after, cursor_pos),
            daemon=True
        )
        self.completion_thread.start()
        
        self.update_status("Requesting AI completion...")
    
    def _get_completion_async(self, context_before: str, current_line: str, context_after: str, cursor_pos: str):
        """Get AI completion asynchronously."""
        print(f"[DEBUG] Editor: _get_completion_async started")
        
        if not self.ai_engine:
            print(f"[DEBUG] Editor: No AI engine available")
            return
            
        try:
            completion = self.ai_engine.get_completion(context_before, current_line, context_after)
            print(f"[DEBUG] Editor: Got completion result: {completion}")
            
            # Get chat info for display
            request_prompt, response_text = self.ai_engine.get_last_chat_info()
            print(f"[DEBUG] Editor: Chat info - Request length: {len(request_prompt) if request_prompt else 0}")
            print(f"[DEBUG] Editor: Chat info - Response: '{response_text}'")
            
            # Schedule UI updates on main thread
            if request_prompt:
                self.root.after(0, self._update_chat_request, request_prompt)
            if response_text:
                self.root.after(0, self._update_chat_response, response_text)
            
            if completion and completion.strip():
                # Schedule completion display
                print(f"[DEBUG] Editor: Scheduling completion display")
                self.root.after(0, self._show_completion, completion, cursor_pos)
            else:
                print(f"[DEBUG] Editor: No completion to display")
                self.root.after(0, lambda: self.update_status("No completion available"))
                
        except Exception as e:
            print(f"[DEBUG] Editor: Exception in _get_completion_async: {e}")
            self.root.after(0, lambda: self.update_status(f"Completion error: {str(e)}"))
    
    def _show_completion(self, completion: str, cursor_pos: str):
        """Show the AI completion as ghost text."""
        print(f"[DEBUG] Editor: _show_completion called with: '{completion}'")
        
        # Verify cursor is still at the same position
        current_cursor_pos = self.text_editor.index(tk.INSERT)
        print(f"[DEBUG] Editor: Expected cursor: {cursor_pos}, Actual: {current_cursor_pos}")
        if current_cursor_pos != cursor_pos:
            print(f"[DEBUG] Editor: Cursor moved, not showing completion")
            return
        
        # Clear any existing ghost text
        self.clear_ghost_text()
        
        # Clean the completion
        completion = completion.strip()
        if not completion:
            print(f"[DEBUG] Editor: Empty completion after strip")
            return
        
        # Get the current line to see what user has already typed
        cursor_line_num = int(cursor_pos.split('.')[0])
        line_start = f"{cursor_line_num}.0"
        current_line_text = self.text_editor.get(line_start, cursor_pos)
        
        # Extract the word/token that the user is currently typing
        # This is typically the last word on the line
        words = current_line_text.split()
        current_word = words[-1] if words else ""
        
        print(f"[DEBUG] Editor: Current line: '{current_line_text}'")
        print(f"[DEBUG] Editor: Current word: '{current_word}'")
        print(f"[DEBUG] Editor: Full completion: '{completion}'")
        
        # Try to find the overlap between what user typed and the completion
        trimmed_completion = self._trim_completion_overlap(current_word, completion)
        
        print(f"[DEBUG] Editor: Trimmed completion: '{trimmed_completion}'")
        
        if not trimmed_completion:
            print(f"[DEBUG] Editor: No additional completion to show")
            return
        
        # Insert ghost text at cursor
        self.text_editor.insert(cursor_pos, trimmed_completion, "ghost_text")
        self.ghost_text_start_pos = cursor_pos
        self.current_completion = trimmed_completion
        
        # Keep cursor at original position
        self.text_editor.mark_set(tk.INSERT, cursor_pos)
        
        self.update_status(f"Completion ready - Press Tab to accept, or keep typing to dismiss")
        self._update_ai_stats()
    
    def _trim_completion_overlap(self, current_word: str, completion: str) -> str:
        """
        Remove the overlapping part between what user typed and the AI completion.
        
        Args:
            current_word: The word/token user is currently typing
            completion: The full completion from AI
            
        Returns:
            The part of completion that extends beyond what user already typed
        """
        if not current_word:
            return completion
        
        # Try different strategies to find the overlap
        
        # Strategy 1: Completion starts with the current word (most common case)
        if completion.lower().startswith(current_word.lower()):
            trimmed = completion[len(current_word):]
            print(f"[DEBUG] Trim: Strategy 1 - starts with current word: '{trimmed}'")
            return trimmed
        
        # Strategy 2: Find the current word anywhere in the completion
        completion_lower = completion.lower()
        current_word_lower = current_word.lower()
        
        if current_word_lower in completion_lower:
            # Find the position and take everything after
            pos = completion_lower.find(current_word_lower)
            trimmed = completion[pos + len(current_word):]
            print(f"[DEBUG] Trim: Strategy 2 - found word in completion: '{trimmed}'")
            return trimmed
        
        # Strategy 3: Check if current word is a prefix of a word in completion
        completion_words = completion.split()
        for word in completion_words:
            if word.lower().startswith(current_word_lower):
                # Found a word that starts with current_word
                remaining_of_word = word[len(current_word):]
                # Get all words after this word too
                word_index = completion_words.index(word)
                remaining_words = completion_words[word_index + 1:]
                
                if remaining_words:
                    trimmed = remaining_of_word + " " + " ".join(remaining_words)
                else:
                    trimmed = remaining_of_word
                    
                print(f"[DEBUG] Trim: Strategy 3 - prefix match: '{trimmed}'")
                return trimmed
        
        # Strategy 4: No clear overlap found, show full completion
        print(f"[DEBUG] Trim: Strategy 4 - no overlap found, showing full completion")
        return completion
    
    def update_line_numbers(self):
        """Update line numbers display."""
        # Get total lines
        total_lines = int(self.text_editor.index('end-1c').split('.')[0])
        
        # Generate line numbers
        line_numbers_text = '\n'.join(str(i) for i in range(1, total_lines + 1))
        
        # Update line numbers widget
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')
    
    def update_status(self, message: str):
        """Update the status bar."""
        self.status_label.config(text=message)
    
    def _update_ai_stats(self):
        """Update AI statistics display."""
        if self.ai_engine:
            stats = self.ai_engine.get_stats()
            stats_text = f"Cache: {stats['cache_size']} | Model: {stats['model']}"
            self.ai_stats_label.config(text=stats_text)
    
    def _update_chat_request(self, request_text: str):
        """Update the chat request display with alternating colors and flash effect."""
        # Flash effect - black background briefly
        self.request_text.config(bg="black")
        self.root.after(100, lambda: self.request_text.config(bg="white"))
        
        # Toggle color: False = green, True = black
        self.chat_color_toggle = not self.chat_color_toggle
        color = "green" if not self.chat_color_toggle else "black"
        
        print(f"[DEBUG] Chat: Request color toggle: {self.chat_color_toggle}, using color: {color}")
        
        # Configure text widget to be editable
        self.request_text.config(state='normal')
        
        # Clear previous content (replace instead of append)
        self.request_text.delete('1.0', 'end')
        
        # Truncate the request message at a meaningful point
        truncated_request = self._truncate_request_message(request_text)
        
        # Insert the new request with color and timestamp
        self.request_text.insert('end', f"[REQUEST {time.strftime('%H:%M:%S')}]\n\n")
        self.request_text.insert('end', f"{truncated_request}\n")
        
        # Apply color to entire content
        self.request_text.tag_add("current_request", '1.0', 'end')
        self.request_text.tag_configure("current_request", foreground=color)
        
        # Scroll to bottom and make read-only
        self.request_text.see('end')
        self.request_text.config(state='disabled')
    
    def _truncate_request_message(self, request_text: str) -> str:
        """Truncate the request message at the appropriate ending point."""
        # Find the line that ends with "...no explanations."
        lines = request_text.split('\n')
        truncated_lines = []
        
        for line in lines:
            truncated_lines.append(line)
            # Stop after the line containing "no explanations"
            if "no explanations" in line.lower():
                break
        
        return '\n'.join(truncated_lines)
    
    def _update_chat_response(self, response_text: str):
        """Update the chat response display with matching colors and flash effect."""
        # Flash effect - black background briefly
        self.response_text.config(bg="black")
        self.root.after(100, lambda: self.response_text.config(bg="white"))
        
        # Use same color as the current request
        color = "green" if not self.chat_color_toggle else "black"
        
        print(f"[DEBUG] Chat: Response using color: {color}")
        
        # Configure text widget to be editable
        self.response_text.config(state='normal')
        
        # Clear previous content (replace instead of append)
        self.response_text.delete('1.0', 'end')
        
        # Insert the new response with matching color and timestamp
        self.response_text.insert('end', f"[RESPONSE {time.strftime('%H:%M:%S')}]\n\n")
        self.response_text.insert('end', f"{response_text}\n")
        
        # Apply color to entire content
        self.response_text.tag_add("current_response", '1.0', 'end')
        self.response_text.tag_configure("current_response", foreground=color)
        
        # Scroll to bottom and make read-only
        self.response_text.see('end')
        self.response_text.config(state='disabled')
    
    def clear_chat_windows(self):
        """Clear both chat request and response windows."""
        # Clear request window
        self.request_text.config(state='normal')
        self.request_text.delete('1.0', 'end')
        self.request_text.config(state='disabled')
        
        # Clear response window
        self.response_text.config(state='normal')
        self.response_text.delete('1.0', 'end')
        self.response_text.config(state='disabled')
        
        # Reset color toggle
        self.chat_color_toggle = False
        
        self.update_status("Chat windows cleared")
    
    # File operations
    def new_file(self):
        """Create a new file."""
        self.text_editor.delete('1.0', 'end')
        self.clear_ghost_text()
        self.update_status("New file created")
    
    def open_file(self):
        """Open a Python file."""
        file_path = filedialog.askopenfilename(
            title="Open Python File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.text_editor.delete('1.0', 'end')
                self.text_editor.insert('1.0', content)
                self.clear_ghost_text()
                self.update_line_numbers()
                self.update_status(f"Opened: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        """Save the current file."""
        file_path = filedialog.asksaveasfilename(
            title="Save Python File",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Get text without ghost text
                content = self.text_editor.get('1.0', 'end-1c')
                
                # Remove ghost text if present
                if self.ghost_text_start_pos:
                    cursor_pos = self.text_editor.index(tk.INSERT)
                    self.clear_ghost_text()
                    self.text_editor.mark_set(tk.INSERT, cursor_pos)
                    content = self.text_editor.get('1.0', 'end-1c')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.update_status(f"Saved: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """AI Python Code Assistant - Educational Demo

This is a simple demonstration of AI-powered code completion 
techniques used by modern coding assistants like GitHub Copilot.

Features:
• AI-powered code completion using OpenAI
• Ghost text preview of completions
• Smart context-aware suggestions
• Debouncing to optimize API usage
• Caching for better performance
• Chat request/response display windows

Instructions:
• Type Python code to get AI completions
• Ghost text appears as grayed italic text
• Press Tab to accept a completion
• Continue typing to dismiss suggestions
• Press Ctrl+Space to manually trigger completion
• Watch the chat windows to see AI communication
• Text colors alternate (green/black) for each request

Created for educational purposes to demonstrate
AI coding assistant principles."""
        
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point for the AI coding assistant."""
    root = tk.Tk()
    app = CodeEditor(root)
    
    # Set window icon if available
    try:
        root.iconbitmap('icon.ico')
    except:
        pass  # Icon file not found, use default
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()
