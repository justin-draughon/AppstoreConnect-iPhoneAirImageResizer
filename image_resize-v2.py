import os
import platform
import subprocess

TARGET_W = 1284
TARGET_H = 2778
PREFIX = "RESIZE - "
VALID_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp")


def list_images():
    return [
        f for f in os.listdir(".")
        if os.path.isfile(f)
        and f.lower().endswith(VALID_EXT)
        and not f.startswith(PREFIX)
    ]


def run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


# ---------------- macOS (sips) ----------------
def resize_macos_sips(files):
    # Uses macOS built-in `sips`. Tries to keep the original format by keeping the same extension.
    for f in files:
        out = PREFIX + f

        # --resampleHeightWidth forces exact HxW (stretch) and --out writes new file
        r = run(["sips", "--resampleHeightWidth", str(TARGET_H), str(TARGET_W), f, "--out", out])

        if r.returncode == 0:
            print(f"Resized: {f} -> {out}")
        else:
            err = (r.stderr or r.stdout).strip()
            print(f"Failed: {f}\n{err}")


# ---------------- Windows (PowerShell + System.Drawing) ----------------
def ps_quote(s: str) -> str:
    # Wrap in single quotes and escape embedded single quotes for PowerShell
    return "'" + s.replace("'", "''") + "'"


def resize_windows_powershell(files):
    # System.Drawing can save JPG/PNG/BMP/GIF/TIFF, but NOT reliably WebP.
    # Because you require "same type as original", we skip WebP on Windows.
    ps_script = r"""
$InPath  = $args[0]
$OutPath = $args[1]
$W       = [int]$args[2]
$H       = [int]$args[3]

Add-Type -AssemblyName System.Drawing

$img = $null
$bmp = $null
$g   = $null

try {
    $img = [System.Drawing.Image]::FromFile($InPath)

    $bmp = New-Object System.Drawing.Bitmap $W, $H
    $g = [System.Drawing.Graphics]::FromImage($bmp)

    $g.InterpolationMode   = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.SmoothingMode       = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.PixelOffsetMode     = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $g.CompositingQuality  = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality

    # Stretch to exact size
    $g.DrawImage($img, 0, 0, $W, $H)

    $ext = [System.IO.Path]::GetExtension($OutPath).ToLower()
    switch ($ext) {
      ".jpg"  { $fmt = [System.Drawing.Imaging.ImageFormat]::Jpeg }
      ".jpeg" { $fmt = [System.Drawing.Imaging.ImageFormat]::Jpeg }
      ".png"  { $fmt = [System.Drawing.Imaging.ImageFormat]::Png }
      ".bmp"  { $fmt = [System.Drawing.Imaging.ImageFormat]::Bmp }
      ".gif"  { $fmt = [System.Drawing.Imaging.ImageFormat]::Gif }
      ".tif"  { $fmt = [System.Drawing.Imaging.ImageFormat]::Tiff }
      ".tiff" { $fmt = [System.Drawing.Imaging.ImageFormat]::Tiff }
      default { throw "Unsupported output extension for System.Drawing: $ext" }
    }

    $bmp.Save($OutPath, $fmt)
}
finally {
    if ($g)   { $g.Dispose() }
    if ($bmp) { $bmp.Dispose() }
    if ($img) { $img.Dispose() }
}
"""

    for f in files:
        ext = os.path.splitext(f)[1].lower()

        if ext == ".webp":
            print(f"Skipped (Windows cannot reliably write WebP without extra codecs/tools): {f}")
            continue

        out = PREFIX + f
        in_path = os.path.abspath(f)
        out_path = os.path.abspath(out)

        # Build a single PowerShell command string and pass args positionally ($args)
        cmd_str = f"& {{ {ps_script} }} {ps_quote(in_path)} {ps_quote(out_path)} {TARGET_W} {TARGET_H}"

        r = run([
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-Command", cmd_str
        ])

        if r.returncode == 0:
            print(f"Resized: {f} -> {out}")
        else:
            err = (r.stderr or r.stdout).strip()
            print(f"Failed: {f}\n{err}")


def main():
    files = list_images()
    if not files:
        print("No images found to resize (or all already resized).")
        return

    system = platform.system()

    if system == "Darwin":
        resize_macos_sips(files)
    elif system == "Windows":
        resize_windows_powershell(files)
    else:
        print(f"Unsupported OS: {system}. This script supports only Windows and macOS.")


if __name__ == "__main__":
    main()
