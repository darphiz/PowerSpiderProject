import re
import os
import zipfile
import shutil
from PIL import Image
import mimetypes

def format_list(lists):
    try:
        if not lists:
            return None
        if not isinstance(lists, list):
            lists = [lists]
        _set = {"\"" + x + "\"" for x in lists}
        _set = str(_set).replace("'", "")
        return _set
    except Exception:
        return None

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
                # break


def delete_all_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        


def move_file_to_folder(file_path, folder_path):
    # Make sure the file exists
    if not os.path.isfile(file_path):
        print(f"{file_path} does not exist")
        return

    # Make sure the folder exists
    if not os.path.isdir(folder_path):
        print(f"{folder_path} does not exist")
        return

    # Get the filename and destination path
    filename = os.path.basename(file_path)
    destination_path = os.path.join(folder_path, filename)

    # Move the file to the destination folder
    shutil.move(file_path, destination_path)

    print(f"Moved {filename} to {folder_path}")



def check_folder(folder_path):
    broken_files = []
    files = os.listdir(folder_path)
    for counter,file_name in enumerate(files):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and os.path.getsize(file_path) == 0:
            broken_files.append(file_name)
        print(f"Checked {counter}/{len(files)} files")
    return broken_files





def is_svg_file(filename):
    """Returns True if the file is an SVG image, False otherwise."""
    mime_type, _ = mimetypes.guess_type(filename)
    print(mime_type)
    return mime_type == 'image/svg+xml'
all_svg = 0

def correct_image_format(image_path):
    try:
        with Image.open(image_path) as img:
            img_format = img.format
    except Exception as e:
        img_format = "SVG"
    file_ext = os.path.splitext(image_path)[1]
    if file_ext != '.' + img_format.lower():
        if img_format == "JPEG":
            img_format = "JPG"
        new_image_path = os.path.splitext(image_path)[0] + '.' + img_format.lower()
        return new_image_path
    return image_path

def all_images(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            correct_image_format(file_path)
    print(all_svg)
def reverse_list(string):
    return re.findall(r'"([^"]*)"', string)


def re_arrange_order(formated_list):
    unformatted_list = reverse_list(formated_list)
    # make the first element the last element
    unformatted_list.append(unformatted_list.pop(0))
    return format_list(unformatted_list)

if __name__ == "__main__":
    # all_images("sorter/source/gs_images")
    # broken = check_folder("sorter/source/gs_images")
    # print(broken)
    # print(len(broken))
    # # write broken files to a text file
    # with open("broken_files.txt", "w") as f:
    #     for file_name in broken:
    #         f.write(format_list([file_name]) + "\n")
    
    un = '{"turning-for-home-inc_d2462499-58ba-495f-8c50-ef6418955f13.png", "turning-for-home-inc_87b759c5-f9fe-4bfe-a5e0-7ed62e15e062.jpeg"}'
    
    print(re_arrange_order(un))
    
    # zip_directory('sorter/source', '/mnt/d/latest_image_chunk_4.zip')
    # zip_directory('sorter/source', '/mnt/d/gs_images_chunk_5.zip')

    # move_file_to_folder("/home/scraper1/Downloads/gs_images_chunk_4.zip", "/mnt/d/")
    # delete_all_files_in_folder("/mnt/d/")
