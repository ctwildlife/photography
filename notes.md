NAVIGATION

pwd                     # Show current folder path
dir                     # List files/folders in current folder
ls                      # Another way to list files
cd <folder>             # Change directory into <folder>
cd ..                   # Go up one folder
ls -Recurse             # List all files in current folder + subfolders


FILE AND FOLDER MANAGEMENT

mkdir <folder>          # Create a new folder
rm <file>               # Delete a file
del <file>              # Alternate delete (works in PowerShell)
rmdir <folder>          # Delete empty folder
rm -r <folder>          # Delete folder + contents recursively
copy <source> <dest>    # Copy file
move <source> <dest>    # Move or rename file


VIEWING AND EDITING FILES 

type <file>             # Show file contents in terminal
Get-Content <file>      # Another way to view file contents
echo "text" > file.txt  # Create a new file with "text"
echo "more text" >> file.txt  # Append text to a file
code <file>             # Open a file in VS Code from terminal


PYTHON COMMANDS

python generate_galleries.py   # Run your gallery generation script
git add .                      # Stage all changes
git commit -m "message"        # Commit changes
git push                        # Push changes to GitHub

#git add Pages/* or git add . 
#git commit -m "Updated gallery with new photos" 


GALLERY CHECKS

ls photos_web\birds            # List resized images for a category
ls -lh photos_web\birds         # List files with sizes (human-readable)
ls -lt photos_web\birds         # List files sorted by modification time
Get-ChildItem photos_web\birds | Measure-Object -Property Length -Sum  # Total size

