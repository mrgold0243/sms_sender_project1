import py_compile
import os

# Specify the directory containing your .py files
source_dir = 'src'  # Change this to your source directory

# Compile all .py files in the specified directory
for filename in os.listdir(source_dir):
    if filename.endswith('.py'):
        full_path = os.path.join(source_dir, filename)
        py_compile.compile(full_path)
        print(f'Compiled {filename} to bytecode.')
