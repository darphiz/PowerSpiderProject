import os
# from .models import NGO

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
        
def get_files_starting_with_underscore(folder_path):
    for filename in os.listdir(folder_path):
        if filename.startswith('_'):
            yield os.path.join(folder_path, filename)

def delete_files(generator):
    for file_path in generator:
        os.remove(file_path)
  
delete_files(get_files_starting_with_underscore('../images/guidestar'))
  
# def rescrape():
#     bad_images = get_files_starting_with_underscore('../images/guidestar')
#     for image in bad_images:
#         with open('bad_images.txt', 'a') as f:
#             f.write(format_list([image]) + '\n')

# rescrape()

# def bad_images():
#     with open('guidestar_app/bad_images.txt', 'r') as f:
#         for line in f:
#             line = line.strip()
#             if line:
#                 yield line

# def rescrape():
#     print("rescraping...")
#     images = list(bad_images())
#     ng = NGO.objects.filter(image__in=images)    
#     ng.update(resolved=False, locked=False)
#     print("done")