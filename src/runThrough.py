import os

def list_files_and_contents(startpath):
    for root, dirs, files in os.walk(startpath):
        for file in files:
            if file.endswith('.py'):  # Modify this condition for different file types
                path = os.path.join(root, file)
                print(path)
                with open(path, 'r') as f:
                    print(f.read())
                print("\n\n")  # Adding space between files

# Replace 'your_directory_path' with the path of your directory
directory_path = os.getcwd() + "/"
list_files_and_contents(directory_path)
