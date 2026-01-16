import os
import pathspec

def is_binary(file_path):
    """
    Check if a file is binary.
    Reads a small chunk of the file to check for null bytes.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return True
    except Exception:
        return True # Treat read errors as binary/unreadable
    return False

def get_ignore_spec(root_dir):
    """
    Load .gitignore if it exists, otherwise use default ignores.
    """
    gitignore_path = os.path.join(root_dir, '.gitignore')
    patterns = [
        '.git',
        'node_modules',
        '__pycache__',
        'venv',
        'env',
        '*.lock',
        'package-lock.json',
        'dist',
        'build',
        '*.pyc',
        '.DS_Store',
        'contextmesh_snapshot.xml', # Don't ingest the output file itself
        '.env'
    ]
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            patterns.extend(f.read().splitlines())
            
    return pathspec.PathSpec.from_lines('gitwildmatch', patterns)

def generate_xml_context(root_dir):
    """
    Walks the directory and yields file context in XML format as a string.
    This avoids writing to disk if we just want to send it to the API.
    """
    spec = get_ignore_spec(root_dir)
    context_parts = ["<codebase>\n"]
    
    for root, dirs, files in os.walk(root_dir):
        # Prune directories
        dirs[:] = [d for d in dirs if not spec.match_file(os.path.relpath(os.path.join(root, d), root_dir))]
        
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, root_dir)
            
            if spec.match_file(rel_path):
                continue
                
            if is_binary(abs_path):
                continue
            
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as infile:
                    content = infile.read()
                    context_parts.append(f'<file path="{rel_path}">\n')
                    context_parts.append(content)
                    context_parts.append(f'\n</file>\n')
            except Exception as e:
                print(f"Error reading {rel_path}: {e}")

    context_parts.append("</codebase>\n")
    return "".join(context_parts)
