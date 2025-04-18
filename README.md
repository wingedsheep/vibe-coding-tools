# Vibe Coding Tools

A collection of utility tools designed to enhance your vibe coding experience with AI and large language models (LLMs).

## Context File Creator

A desktop application that helps you prepare code files for input into LLMs like ChatGPT and Claude to streamline your vibe coding workflow.

### Features

- **File Selection**: Add individual files or entire folders 
- **Drag and Drop**: Easily drag files or folders into the application
- **Root Folder Detection**: Automatically identifies common root paths
- **Markdown Generation**: Creates formatted markdown with file structure and contents
- **Clipboard Integration**: Copies generated markdown to clipboard

### Usage

1. Select files using buttons or drag and drop
2. Adjust root folder if needed
3. Click "Create Markdown" to generate and copy to clipboard
4. Paste into your preferred AI assistant for vibe coding

### Installation

```bash
# Clone and install
git clone https://github.com/wingedsheep/vibe-coding-tools.git
cd vibe-coding-tools
pip install -r requirements.txt

# Run
python select_context.py
```

### Requirements

- Python 3.6+
- PyQt6
- pyperclip

## License

This project is licensed under the MIT License.