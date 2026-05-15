.PHONY: clean files

clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} +

files:
	@find . \( -path "./venv" -o -name ".?*" \) -prune -o -print
    
