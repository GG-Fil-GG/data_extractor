import os
from prettytable import PrettyTable

def get_project_structure(root_dir, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = ['.git', 'venv', 'temp', '__pycache__']
        
    table = PrettyTable(['Path', 'Type'])
    
    for root, dirs, files in os.walk(root_dir):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for name in dirs:
            table.add_row([os.path.join(root, name), 'Directory'])
        for name in files:
            table.add_row([os.path.join(root, name), 'File'])
    
    return table

root_directory = '/Users/giorgioarangutani/Library/CloudStorage/OneDrive-Personal/My projects/IT and AI/data_extractor'
project_structure = get_project_structure(root_directory)
print(project_structure)
