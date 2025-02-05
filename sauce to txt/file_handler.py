import os
import shutil
import unicodedata
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileHandler(FileSystemEventHandler):
    
    border = "========================="
    
    def __init__(self, watch_dir, archive_dir):
        self.watch_dir = watch_dir
        self.archive_dir = archive_dir
        
        # Track internally created .txt files
        self.system_created_txt_files = set()


    def on_created(self, event):
        if event.is_directory:
            return

        # Normalize filenames to handle utf-8 characters
        relative_path = os.path.relpath(event.src_path, self.watch_dir)
        base_name = unicodedata.normalize('NFC', os.path.basename(event.src_path))
        name_without_ext = unicodedata.normalize('NFC', os.path.splitext(base_name)[0])

        # Create the path for the corresponding .txt file
        txt_path = os.path.join(self.archive_dir, os.path.dirname(relative_path), name_without_ext + ".txt")

        # Ensure the directory for the .txt exists
        os.makedirs(os.path.dirname(txt_path), exist_ok=True)

        # Check if the created file is the corresponding .txt file
        if event.src_path == txt_path:
            return  # Ignore the .txt file created by the program

        # Check if the added file is a .txt file, if so do nothing
        if base_name.endswith(".txt"):
            # Skip system-generated .txt files
            if event.src_path in self.system_created_txt_files:
                return
            print(f"Ignored .txt file: {base_name}")
            print(self.border)
            return

        # Get the current date and time
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Create corresponding .txt file in archive directory
        # As of now I'm thinking that the user will have to input Link by themselves
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"""File name: {base_name}

Link: 
                        
Last updated: {current_date}

Other:
""")
        
        # Track this .txt file as system-generated
        self.system_created_txt_files.add(txt_path)

        # Print confirmation messages
        print(f"File added: {base_name}")
        print("Corresponding source file also created.")
        print(self.border)


    # Handle moved files or name-changes (if needed)
    def on_moved(self, event):
        if event.is_directory:
            return
        
        old_relative_path = os.path.relpath(event.src_path, self.watch_dir)
        new_relative_path = os.path.relpath(event.dest_path, self.watch_dir)

        old_name_without_ext = unicodedata.normalize('NFC', os.path.splitext(os.path.basename(old_relative_path))[0])
        new_name_without_ext = unicodedata.normalize('NFC', os.path.splitext(os.path.basename(new_relative_path))[0])

        old_txt_path = os.path.join(self.archive_dir, os.path.dirname(old_relative_path), old_name_without_ext + ".txt")
        new_txt_path = os.path.join(self.archive_dir, os.path.dirname(new_relative_path), new_name_without_ext + ".txt")

        if os.path.exists(old_txt_path):
            os.makedirs(os.path.dirname(new_txt_path), exist_ok=True)
            shutil.move(old_txt_path, new_txt_path)
    
    # If file is deleted then delete its corresponding file in the other dir
    def on_deleted(self, event):
        # Handle directory deletions in watch_dir
        if event.is_directory:
            relative_dir_path = os.path.relpath(event.src_path, self.watch_dir)
            archive_dir_path = os.path.join(self.archive_dir, relative_dir_path)

            if os.path.exists(archive_dir_path):
                shutil.rmtree(archive_dir_path) # Remove the entire directory and its contents
                print(f"Directory deleted: {relative_dir_path}")
                print("Corresponding source files also deleted.")
                print(self.border)
            return
        
        # Handle individual file deletions in watch_dir
        relative_path = os.path.relpath(event.src_path, self.watch_dir)
        base_name = unicodedata.normalize('NFC', os.path.basename(relative_path))
        name_without_ext = unicodedata.normalize('NFC', os.path.splitext(base_name)[0])

        # Delete the corresponding .txt file in archive_dir if it exists
        txt_path = os.path.join(self.archive_dir, os.path.dirname(relative_path), name_without_ext + ".txt")
        if os.path.exists(txt_path):
            os.remove(txt_path)
            print(f"File deleted: {base_name}")
            print("Corresponding source file also deleted.")
            print(self.border)

        # If .txt file is deleted in archive_dir, delete the corresponding file in watch_dir
        # NOT ADVISED as this process will take longer, how much longer depends on the size of watch_dir
        if base_name.endswith(".txt"):
            # List of possible file extensions in watch_dir
            possible_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.gif', '.jpeg', '.jpg', '.png', '.webp', '.mp3', '.aac', '.wav', '.flac', '.bmp']    # Extend this list as needed

            # Normalize the corresponding watch_dir file path
            name_without_ext = os.path.splitext(base_name)[0]

            # Loop through the extensions and check if a corresponding file exists in watch_dir
            for ext in possible_extensions:
                watch_file_path = os.path.join(self.watch_dir, os.path.dirname(relative_path), name_without_ext + ext)
                if os.path.exists(watch_file_path):
                    os.remove(watch_file_path)
                    print(f"File deleted: {base_name}")
                    print(f"Watch file also deleted: {name_without_ext}{ext}")
                    print(self.border)
                    break   # Exit the loop once the file is found and deleted

# Main method
if __name__ == "__main__":
    watch_dir = r"E:\source2txt test\video archive dir"         # Your watch directory
    archive_dir = r"E:\source2txt test\.txt archive dir"        # Your archive directory

    # Create the directory if they do not exist
    for dir in [watch_dir, archive_dir]:
        if not os.path.exists(dir):
            os.makedirs(dir)
    
    # Set up the observer
    event_handler = FileHandler(watch_dir, archive_dir)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=True)
    observer.schedule(event_handler, archive_dir, recursive=True)

    # Start monitoring
    observer.start()

    try:
        while True:
            pass  # Keep the program running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
