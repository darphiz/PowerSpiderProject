# import shutil

# if __name__ == '__main__':
#     output_filename = "guidestar_app"
#     dir_name = "images/guidestar"
#     shutil.make_archive(output_filename, 'zip', dir_name)
    
    
    
import os
import zipfile

def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, mode='w') as zipf:
        len_dir_path = len(folder_path)
        for root, _, files in os.walk(folder_path):
            counter = 0
            total_files = len(files)
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path[len_dir_path:])
                counter += 1
                print(f"Zipped {counter}/{total_files} files")
                
zip_directory('images/guidestar', 'guidestar_chunk_1.zip')