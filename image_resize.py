import sys
import subprocess
import os

# --- Ensure Pillow is installed ---
try:
    from PIL import Image
except ImportError:
    print("Pillow not found. Installing Pillow...")
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "pillow"
    ])
    from PIL import Image

# --- Resize settings ---
TARGET_WIDTH = 1284
TARGET_HEIGHT = 2778
PREFIX = "RESIZE - "
VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")

def resize_images_in_folder():
    for filename in os.listdir("."):
        if not filename.lower().endswith(VALID_EXTENSIONS):
            continue

        if filename.startswith(PREFIX):
            continue

        try:
            with Image.open(filename) as img:
                resized = img.resize(
                    (TARGET_WIDTH, TARGET_HEIGHT),
                    Image.Resampling.LANCZOS
                )

                new_filename = PREFIX + filename
                resized.save(new_filename)

                print(f"Resized: {filename} → {new_filename}")

        except Exception as e:
            print(f"Skipped {filename}: {e}")

if __name__ == "__main__":
    resize_images_in_folder()
