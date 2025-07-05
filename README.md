# AI Coding Assistant - Educational Demo

A minimal Python code editor with AI-powered completion to demonstrate how modern coding assistants like GitHub Copilot and Cursor work.

## Features

🤖 **AI Code Completion**: Uses OpenAI's API to provide intelligent code suggestions
👻 **Ghost Text Preview**: Shows completions as grayed-out text before accepting
⚡ **Smart Debouncing**: Optimizes API calls to avoid excessive requests
💾 **Caching**: Stores recent completions for better performance
🎯 **Context-Aware**: Sends surrounding code for better completion quality
💬 **Chat Display**: Shows AI request/response communication with alternating colors
✨ **Flash Effect**: Windows flash black briefly to emphasize new messages
📝 **Smart Truncation**: Request messages truncated at meaningful stopping points

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Edit `config.json` and add your OpenAI API key:

```json
{
    "openai_api_key": "your-actual-openai-api-key-here",
    "model": "gpt-3.5-turbo",
    "max_tokens": 100,
    "temperature": 0.3,
    "completion_delay_ms": 500,
    "context_lines_before": 10,
    "context_lines_after": 5
}
```

### 3. Run the Application

```bash
python code_editor.py
```

## How It Works

### AI Completion Engine (`ai_completion_engine.py`)

This module demonstrates key techniques used by modern AI coding assistants:

1. **Debouncing**: Prevents excessive API calls by waiting 500ms between requests
2. **Context Building**: Sends 10 lines before and 5 lines after the cursor for better context
3. **Caching**: Stores recent completions to avoid redundant API calls
4. **Smart Prompting**: Uses carefully crafted prompts for better code completion

### Code Editor (`code_editor.py`)

The editor implements:

1. **Ghost Text Rendering**: Shows AI suggestions as gray, italic text
2. **Non-blocking Requests**: Uses threading to avoid freezing the UI
3. **Smart Triggering**: Only requests completions at appropriate times
4. **Tab Acceptance**: Press Tab to accept suggestions

## Usage

1. **Start Typing**: Type Python code in the editor
2. **See Suggestions**: Ghost text appears as gray, italic text
3. **Accept Completions**: Press Tab to accept the suggestion
4. **Dismiss Suggestions**: Continue typing to dismiss
5. **Monitor Communication**: Watch the chat windows below the editor
   - Windows flash black briefly when new messages arrive
   - Colors alternate between green and black for each request/response pair
   - Request messages are truncated for readability
6. **Manual Trigger**: Press Ctrl+Space to force a completion request
7. **Clear Chat**: Use the "Clear Chat" button to reset the communication log

## Educational Concepts Demonstrated

### 1. Debouncing Pattern
```python
def _should_debounce(self) -> bool:
    current_time = time.time() * 1000
    delay_ms = self.config.get('completion_delay_ms', 500)
    
    if current_time - self._last_request_time < delay_ms:
        return True
    
    self._last_request_time = current_time
    return False
```

### 2. Context-Aware Prompting
```python
def _build_completion_prompt(self, context_before: str, cursor_line: str, context_after: str) -> str:
    prompt = f"""You are an AI coding assistant. Complete the Python code at the cursor position.

Context before:
{context_before}

Current line (cursor at end): {cursor_line}

Context after:
{context_after}

Complete the code at the cursor position..."""
    return prompt
```

### 3. Ghost Text Implementation
```python
# Insert completion as ghost text
self.text_editor.insert(cursor_pos, completion, "ghost_text")
self.text_editor.tag_configure("ghost_text", foreground="gray", font=("Consolas", 11, "italic"))

# Accept completion by removing the tag
self.text_editor.tag_remove("ghost_text", start_pos, end_pos)
```

### 4. Chat Communication Display
```python
def _update_chat_request(self, request_text: str):
    # Toggle color: False = green, True = black
    self.chat_color_toggle = not self.chat_color_toggle
    color = "green" if not self.chat_color_toggle else "black"
    
    # Display with timestamp and alternating colors
    self.request_text.insert('end', f"[REQUEST {time.strftime('%H:%M:%S')}]\n")
    self.request_text.tag_configure(tag_name, foreground=color)
```

### 5. Efficient Caching
```python
def _create_cache_key(self, context_before: str, context_after: str, cursor_line: str) -> str:
    combined = f"{context_before[-100:]}{cursor_line}{context_after[:50:]}"
    return combined.replace(' ', '').replace('\n', '')
```

## Configuration Options

- `completion_delay_ms`: Debounce delay in milliseconds (default: 500)
- `context_lines_before`: Lines of context before cursor (default: 10)
- `context_lines_after`: Lines of context after cursor (default: 5)
- `max_tokens`: Maximum tokens in completion (default: 100)
- `temperature`: AI creativity level (default: 0.3)

## Architecture Overview

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   Code Editor UI    │    │  AI Completion       │    │   OpenAI API    │
│                     │    │  Engine              │    │                 │
│ • Ghost Text        │◄──►│                      │◄──►│ • GPT-3.5-turbo │
│ • Event Handling    │    │ • Debouncing         │    │ • Code Context  │
│ • Context Extract   │    │ • Caching            │    │ • Completions   │
│ • Threading         │    │ • Prompt Engineering │    │                 │
└─────────────────────┘    └──────────────────────┘    └─────────────────┘
```

## Key Learning Points

1. **Debouncing**: Essential for API efficiency and user experience
2. **Context Management**: More context = better completions, but costs more
3. **Ghost Text UX**: Non-intrusive way to preview suggestions
4. **Async Operations**: Keep UI responsive during API calls
5. **Caching Strategy**: Balance memory usage with API cost savings
6. **Prompt Engineering**: Clear, structured prompts yield better results

## Extending the Demo

Future enhancements could include:

- **Multi-language support**: Extend beyond Python
- **Inline documentation**: Show API docs with completions
- **Code analysis**: Highlight potential errors
- **Usage analytics**: Track completion acceptance rates
- **Multiple suggestions**: Show alternative completions
- **Intelligent ranking**: Learn from user preferences

## Troubleshooting

### "Configuration Error" on startup
- Check that `config.json` exists and has valid JSON
- Ensure your OpenAI API key is set correctly

### No completions appearing
- Verify your API key has credits
- Check internet connection
- Ensure you're typing at the end of a line with some content

### Slow performance
- Increase `completion_delay_ms` in config
- Reduce `context_lines_before` and `context_lines_after`
- Check your internet connection speed

## Educational Use

This demo is designed for:
- Computer Science students learning AI integration
- Developers understanding modern IDE features  
- AI enthusiasts exploring practical applications
- Teachers demonstrating real-world coding assistant concepts

The code prioritizes clarity and educational value over performance optimization.
