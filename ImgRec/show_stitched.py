import matplotlib
matplotlib.use('TkAgg')  # Use the TkAgg backend
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import importlib.util
import math
from datetime import datetime
import shutil

config_dir = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(config_dir, 'PC_CONFIG.py')
spec = importlib.util.spec_from_file_location("PC_CONFIG", config_path)
PC_CONFIG = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PC_CONFIG)

def showAnnotatedStitched():
    image_dir = os.path.join(PC_CONFIG.FILE_DIRECTORY,"image-rec","annotated_images")
    image_files = [os.path.join(image_dir, filename) for filename in os.listdir(image_dir) if filename.endswith(".jpg")]
    
    # Adjust the layout to 2 by 4
    num_cols = 4  # Number of columns
    num_rows = 2  # Number of rows
    
    # Ensure there is at least one row if there are images
    num_rows = max(1, math.ceil(len(image_files) / num_cols)) if image_files else 1

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(num_cols * 3, num_rows * 3), dpi=150)

    # Check if there are any images to display
    if image_files:
        for i, ax in enumerate(axes.flat):
            if i < len(image_files):
                img = mpimg.imread(image_files[i])
                ax.imshow(img)
                ax.axis("off")
            else:
                ax.axis("off")
    else:
        # If no images, just hide all axes as there's nothing to display
        for ax in axes.flat:
            ax.axis("off")

    plt.subplots_adjust(wspace=0, hspace=0)
    plt.tight_layout(pad=0, h_pad=0, w_pad=0)

    stitched_image_dir = os.path.join(PC_CONFIG.FILE_DIRECTORY, "image-rec", "stitched_images")
    stitched_file_name = generate_filename_with_timestamp()
    save_path = os.path.join(stitched_image_dir, stitched_file_name)
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
    print(f"Figure saved to {save_path}")

    manager = plt.get_current_fig_manager()
    manager.window.wm_geometry("+0+0")  # Move the window to position (0, 0)

    # plt.show()
    archive_directory_content(image_dir)

def generate_filename_with_timestamp(prefix="stitched_image", extension=".jpg"):
    # Get the current date and time
    now = datetime.now()
    # Format the date and time as a string
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    # Combine prefix, timestamp, and extension to form the filename
    filename = f"{prefix}_{timestamp}{extension}"
    return filename

def archive_directory_content(directory_path):
    # Moves files with the specified extension from the given directory to an archive directory,
    # except for files named .gitkeep.

    archive_dir= os.path.join(PC_CONFIG.FILE_DIRECTORY,"image-rec","annotated_archive")
    file_extension=".jpg"
    os.makedirs(archive_dir, exist_ok=True)  # Create the archive directory if it doesn't exist
    
    for filename in os.listdir(directory_path):
        if filename.endswith(file_extension) and filename != ".gitkeep":
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            new_filename = f"{filename.rsplit('.', 1)[0]}_{timestamp}.{filename.rsplit('.', 1)[1]}"
            src_path = os.path.join(directory_path, filename)
            dest_path = os.path.join(archive_dir, new_filename)
            shutil.move(src_path, dest_path)
            print(f"Moved and renamed: {src_path} to {dest_path}")

if __name__ == "__main__":
    # Example usage
    showAnnotatedStitched()