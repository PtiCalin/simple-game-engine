"""
Markdown Helper for RPG Data (Obsidian integration)
"""
import re

def extract_code_blocks(md_text, block_type='yaml'):
    pattern = rf'```{block_type}([\s\S]+?)```'
    return re.findall(pattern, md_text)

# Example: extract YAML blocks from Obsidian markdown
# blocks = extract_code_blocks(md_content, 'yaml')
