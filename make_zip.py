import os
import zipfile

def create_project_zip():
    output_filename = "TravelSphere.zip"
    excluded_dirs = {'__pycache__', 'staticfiles', '.idea', '.vscode', 'node_modules'}
    excluded_extensions = ('.pyc', '.pyo', '.zip', '.tar', '.gz')

    # Remove existing zip first
    if os.path.exists(output_filename):
        try:
            os.remove(output_filename)
        except Exception:
            pass

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for file in files:
                if file == output_filename or file.endswith(excluded_extensions):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)

    size_mb = os.path.getsize(output_filename) / (1024 * 1024)
    print(f"Created {output_filename} successfully! Size: {size_mb:.2f} MB (includes .git repository history)")

if __name__ == '__main__':
    create_project_zip()
