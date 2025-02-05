import pytest
import os
import shutil
import tempfile
from datetime import datetime
from unittest.mock import patch
from file_handler import FileHandler   # Assume this is your file handler

# Fixture for setup and teardown
@pytest.fixture    
def setup_directories():
    # Create temporary directories for watch_dir and archive_dir
    watch_dir = tempfile.mkdtemp()
    archive_dir = tempfile.mkdtemp()

    # Initialize the FileHandler with the temporary directories
    handler = FileHandler(watch_dir, archive_dir)

    yield watch_dir, archive_dir, handler

    # Teardown - Clean up temporary directories after each test
    shutil.rmtree(watch_dir)
    shutil.rmtree(archive_dir)



### FILE CREATION TESTS

# Test that a file with a standard name (without special chars) in watch_dir creates a correct corresponding .txt file in archive_dir. (CORRUPT JPEG TO TXT)
def test_single_standard_file_creation(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Create a standard file in watch_dir
    file_path = os.path.join(watch_dir, 'testfile.webm')
    with open(file_path, 'w') as f:
        f.write("This is a test file")

    # Trigger the on_created event manually
    handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Check if corresponding .txt file is created in archive_dir
    txt_file = os.path.join(archive_dir, 'testfile.txt')
    assert os.path.exists(txt_file), f"File {txt_file} was not created."


# Test that multiple files created or added in watch_dir generate the correct .txt files in archive_dir.
def test_multiple_standard_files_creation(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Create several standard files in watch_dir
    for i in range(99):
        file_path = os.path.join(watch_dir, f'testfile{i}.webm')
        with open(file_path, 'w') as f:
            f.write("This is a test file")
        
        # Trigger the on_created event manually for each file
        handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())
    
    # Verify that 100 corresponding .txt files are created in archive_dir
    for i in range(99):
        txt_file = os.path.join(archive_dir, f'testfile{i}.txt')
        assert os.path.exists(txt_file), f"File {txt_file} was not created."    


# Test that nested subdirectories in watch_dir have their file properly reflected with corresponding .txt files in archive_dir. Single file. Bottom subdir. (2 subdirs deep)
def test_nested_subdirectory_creation_single(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Create a nested directory in watch_dir
    nested_dir = os.path.join(watch_dir, 'nested', 'subdir')
    os.makedirs(nested_dir) # Create the nested directories

    # Create a standard file in the nested directory
    file_path = os.path.join(nested_dir, 'testfile.webm')
    with open(file_path, 'w') as f:
        f.write("This is a test file in a nested directory")
    
    # Trigger the on_created event manually for the new file
    handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Check if corresponding .txt file is created in the corresponding nested structure of archive_dir
    txt_file = os.path.join(archive_dir, 'nested', 'subdir', 'testfile.txt')
    assert os.path.exists(txt_file), f"File {txt_file} was not created."    


# Test that nested subdirectories in watch_dir have their files properly reflected with corresponding .txt files in archive_dir. Multiple files. Every subdir. (2 subdirs deep)
def test_nested_subdirectory_creation_multiple(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Create a nested directory in watch_dir
    nested_dir = os.path.join(watch_dir, 'nested', 'subdir')
    os.makedirs(nested_dir)  # Create the nested directories

    # Create multiple standard files in the nested directory
    for i in range(10):  # Change this number to match the number of files created
        file_path = os.path.join(nested_dir, f'testfile{i}.webm')
        with open(file_path, 'w') as f:
            f.write(f"This is a test file in a nested directory")

        # Trigger the on_created event manually for each new file
        handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Check if corresponding .txt files are created in the corresponding nested structure of archive_dir
    for i in range(10):  # Change this number to match the number of files created
        txt_file = os.path.join(archive_dir, 'nested', 'subdir', f'testfile{i}.txt')
        assert os.path.exists(txt_file), f"File {txt_file} was not created."


# Test that a .txt file created or added in watch_dir is ignored in archive_dir.
def test_txt_file_ignored_in_watch_dir(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Create a standard file in watch_dir with a .txt extension
    file_path = os.path.join(watch_dir, 'testfile.txt')
    with open(file_path, 'w') as f:
        f.write("This is a test .txt file that should be ignored.")

    # Trigger the on_created event manually for the .txt file
    handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Check that no corresponding .txt file is created in archive_dir
    txt_file = os.path.join(archive_dir, 'testfile.txt')
    assert not os.path.exists(txt_file), f"File {txt_file} should not have been created."


# Test that a file created or added in archive_dir is ignored in watch_dir. (using base_file_name, ignoring extension)
def test_file_created_in_archive_ignored_in_watch_dir(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Create a .txt file (arbitrary) in archive_dir
    file_name = 'testfile.txt'
    file_path = os.path.join(archive_dir, file_name)
    with open(file_path, 'w') as f:
        f.write("This is a test file in the archive directory.")

    # Trigger the on_created event manually for the new file in archive_dir
    handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Check if there are any files in watch_dir that have the same base name
    base_file_name = os.path.splitext(file_name)[0]  # Get the name without the extension
    matching_files = [f for f in os.listdir(watch_dir) if os.path.splitext(f)[0] == base_file_name]

    # Assert that no matching files exist in the watch_dir
    assert not matching_files, f"File(s) {matching_files} with base name '{base_file_name}' should not have been created in the watch directory."


# Test that files with special characters in their names in watch_dir (all special chars except those forbidden by WINDOWS) have corresponding .txt files created in archive_dir.
def test_special_character_file_creation(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Define filenames with special characters (excluding forbidden ones)
    special_characters = ['@', '#', '$', '%', '^', '&', '(', ')', '_', '-', '+', '=', '!', '~']
    file_names = [f'testfile{char}.webm' for char in special_characters]

    # Create these files in watch_dir
    for file_name in file_names:
        file_path = os.path.join(watch_dir, file_name)
        with open(file_path, 'w') as f:
            f.write("This is a test file with special characters.")

        # Trigger the on_created event manually for each file
        handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Check that corresponding .txt files are created in archive_dir
    for file_name in file_names:
        base_file_name = os.path.splitext(file_name)[0]  # Get the name without the extension
        txt_file_path = os.path.join(archive_dir, f'{base_file_name}.txt')
        assert os.path.exists(txt_file_path), f"File {txt_file_path} was not created."


# Test that when a .txt file in archive_dir is created DUE to a standard file added to watch_dir the terminal SHOULD NOT print "Ignored .txt file: {base_name}"
def test_no_ignore_txt_messages_on_creation_through_watch_dir(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Use a mock to track calls to the print function
    with patch('builtins.print') as mock_print:

        # Create a standard file in watch_dir
        file_path = os.path.join(watch_dir, 'testfile.webm')
        with open(file_path, 'w') as f:
            f.write("This is a test file")
        
        # Trigger the on_created event manually
        handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

        # Check if corresponding .txt file is created in archive_dir
        txt_file = os.path.join(archive_dir, 'testfile.txt')
        assert os.path.exists(txt_file), f"File {txt_file} was not created."

        # Trigger any additional file events related to .txt files in archive_dir
        # This could involve checking if the system processes .txt files after creation
        handler.on_created(type('', (), {'src_path': txt_file, 'is_directory': False})())

        # Ensure the print function was never called with "Ignored .txt file:"
        assert not any("Ignored .txt file" in str(call) for call in mock_print.call_args_list), \
            '"Ignored .txt file:" was printed unexpectedly.'


# Test that when a .txt file in archive_dir is created NOT DUE to a standard file added to watch_dir the terminal SHOULD print "Ignored .txt file: {base_name}"
def test_ignore_txt_messages_on_creation_through_archive_dir(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Use a mock to track calls to the print function
    with patch('builtins.print') as mock_print:

        # Create a .txt file directly in archive_dir
        txt_file_path = os.path.join(archive_dir, 'manual_file.txt')
        with open(txt_file_path, 'w') as f:
            f.write("This is a manually created .txt file.")

        # Trigger the on_created event manually for the .txt file in archive_dir
        handler.on_created(type('', (), {'src_path': txt_file_path, 'is_directory': False})())

        # Ensure the print function was called with "Ignored .txt file: manual_file.txt"
        mock_print.assert_any_call(f"Ignored .txt file: manual_file.txt")

### FILE DELETION TESTS

# Test that when a single file in watch_dir is deleted, the corresponding .txt file in archive_dir is also deleted.
def test_single_file_deletion_watch_dir(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Create a file in watch_dir
    file_path = os.path.join(watch_dir, 'testfile.webm')
    with open(file_path, 'w') as f:
        f.write("This is a test file")

    # Trigger the on_created event manually for the file
    handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Delete the file
    os.remove(file_path)
    handler.on_deleted(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Check if the corresponding .txt file in archive_dir is also deleted
    txt_file = os.path.join(archive_dir, 'testfile.txt')
    assert not os.path.exists(txt_file), f"Expected {txt_file} to be deleted, alas it wasn't"


# Test that when multiple files in watch_dir is deleted, the corresponding .txt files in archive_dir are also deleted.
def test_multiple_file_deletion_watch_dir(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Create several standard files in watch_dir
    for i in range(99):
        file_path = os.path.join(watch_dir, f'testfile{i}.webm')
        with open(file_path, 'w') as f:
            f.write("This is a test file")
        
        # Trigger the on_created event manually for each file
        handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Delete the files and check if corresponding .txt files in archive_dir are also deleted
    for i in range(99):
        # Recreate the file path for each file
        file_path = os.path.join(watch_dir, f'testfile{i}.webm')

        # Delete the file
        os.remove(file_path)    
        handler.on_deleted(type('', (), {'src_path': file_path, 'is_directory': False})())

        # Check if the corresponding .txt file in archive_dir is also deleted
        txt_file = os.path.join(archive_dir, 'testfile.txt')
        assert not os.path.exists(txt_file), f"Expected {txt_file}{i} to be deleted, alas it wasn't"

# Test that deleting .txt file in archive_dir also deletes the corresponding file in watch_dir.
def test_single_file_deletion_archive_dir(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Create a .txt file in archive_dir
    file_path = os.path.join(archive_dir, 'testfile.txt')
    with open(file_path, 'w') as f:
        f.write("This is a test file")

    # Trigger the on_created event manually for the file
    handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Delete the file in archive_dir
    os.remove(file_path)
    handler.on_deleted(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Extract the base name of the deleted file (without the extension)
    base_file_name = os.path.splitext(os.path.basename(file_path))[0]  # Get 'testfile' without extension

    # Check if there is any file in watch_dir that has the same base name
    matching_file = [f for f in os.listdir(watch_dir) if os.path.splitext(f)[0] == base_file_name]

    # Assert that no file with the same base name exists in watch_dir
    assert not matching_file, f"File with base name {base_file_name} still exists in watch_dir: {matching_file}"


# Test that deleting multiple .txt files in archive_dir also deletes the corresponding files in watch_dir
def test_multiple_file_deletion_archive_dir(setup_directories):
    watch_dir, archive_dir, handler = setup_directories

    # Create multiple .txt files in archive_dir
    for i in range(99):
        file_path = os.path.join(archive_dir, f'testfile{i}.txt')
        with open(file_path, 'w') as f:
            f.write("This is a test file")
        
        # Trigger the on_created event manually for the file
        handler.on_created(type('', (), {'src_path': file_path, 'is_directory': False})())

    # Delete the files in archive_dir and ensure corresponding files in watch_dir are deleted
    for i in range(99):
        file_path = os.path.join(archive_dir, f'testfile{i}.txt')
        
        # Delete the file in archive_dir
        os.remove(file_path)
        handler.on_deleted(type('', (), {'src_path': file_path, 'is_directory': False})())

        # Extract the base name of the deleted file (without the extension)
        base_file_name = os.path.splitext(os.path.basename(file_path))[0]  # Get 'testfileX' without extension

        # Check if there is any file in watch_dir that has the same base name
        matching_files = [f for f in os.listdir(watch_dir) if os.path.splitext(f)[0] == base_file_name]

        # Assert that no file with the same base name exists in watch_dir
        assert not matching_files, f"Files with base name {base_file_name} still exist in watch_dir: {matching_files}"


# Test that deleting a .txt file in watch_dir does nothing in archive_dir as it shouldn't have had a corresponding .txt file to begin with.

# Test that deleting a file in a subdirectory of watch_dir deletes the corresponding .txt file in the matching subdirectory of archive_dir.

# Test that deleting a .txt file in a subdirectory of archive_dir deletes the corresponding file in the matching subdirectory of watch_dir.

# Test that deleting an entire subdirectory in watch_dir deletes its corresponding subdirectory and all corresponding .txt files in archive_dir.

# Test that deleting an entire subdirectory in archive_dir deletes its corresponding subdirectory and all corresponding files in watch_dir.

# Test for cases where some files in a subdirectory fail to delete (e.g., due to permissions) while others succeed.
# Will this leave residual .txt files or cause a partial cleanup?


### FILE MOVE AND RENAME TESTS

# Test that renaming a file in watch_dir correctly renames the corresponding .txt file in archive_dir.

# Test that renaming a file in archive_dir renames its corresponding file in watch_dir.

# Test that moving a file from on subdirectory to another in watch_dir moves the correspoding .txt file in archive_dir.

# Test that moving a .txt file in archive_dir moves the corresponding .txt file in watch_dir.

# Test that moving an entire subdirectory in watch_dir moves the corresponding directory in archive_dir.

# Test that moving an entire subdirectory in archive_dir moves the corresponding directory in watch_dir.


### FILE MODIFICATION TESTS

# Test that modifying a file in watch_dir updates the corresponding .txt file's "Last updated" timestamp in archive_dir (MAY NEED TO BE CHANGED FURTHER ON).

# Test that modifyng a .txt file in archive_dir has no effect on watch_dir.


### EDGE CASE TESTS

# Test that creating a zero-byte file (empty file) in watch_dir creates a corresponding .txt file in archive_dir.

# Test that long filenames in watch_dir (near or at the system's maximum filename length) are handled correctly with .txt files in archive_dir.

# Test that creating two files with the same name but different extensions in watch_dir result in correct behavior
# Correct behavior: update the name of both affected .txt files by appending "({file_extension})" to both their names.

# Test that creating a file and then deleting it immediately in watch_dir also deletes the corresponding .txt file in archive_dir.

# Test that creating a very large file in watch_dir still correctly triggers a .txt creation in archive_dir.


### DIRECTORY STRUCTURE TESTS

# Test that creating a new, empty, subdirectory in watch_dir creates a corresponding empty subdirectory in archive_dir

# Test that creating a new, empty, subdirectory in archive_dir creates a corresponding empty subdirectory in watch_dir

# Test that nested directory structures in watch_dir are mirrored correctly in archive_dir. (MAY BE PRONE TO ERROR DUE TO "({file_extension})" EXCEPTION)


### UNICODE AND SPECIAL CHARACTER HANDLING TESTS

# Test that files with emoji in their names in watch_dir correctly generate .txt files in archive_dir.

# Test that files with spaces in their names in watch_dir correctly generate .txt files in archive_dir.

# Test that files with non-printable Unicode characters (e.g., Zero-width Space, etc.) in their names in watch_dir correctly generate .txt files in archive_dir.

# Test that files with mixed-scripts (e.g., combining Latin, Japanese, and special characters) in their names correctly generate .txt files in archive_dir.

if __name__ == "__main__":
    pytest.main()