Write-Host "AI Coding Assistant - Educational Demo" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Starting the application with debug output..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Instructions for testing:" -ForegroundColor Cyan
Write-Host "1. Type some Python code (e.g., 'def hello():')" -ForegroundColor White  
Write-Host "2. Watch the console for debug messages" -ForegroundColor White
Write-Host "3. Press Ctrl+Space to manually trigger completion" -ForegroundColor White
Write-Host "4. Press Tab to accept completions" -ForegroundColor White
Write-Host ""
Write-Host "The console will show debug information about:" -ForegroundColor Cyan
Write-Host "- When completions are triggered" -ForegroundColor White
Write-Host "- What context is sent to AI" -ForegroundColor White
Write-Host "- What responses are received" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to start..." -ForegroundColor Yellow
Read-Host

python code_editor.py
