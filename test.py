import subprocess

photo = r"C:\Users\Colin Tiernan\Desktop\website-photos\landscapes\cellphone-landscapes\100822-cellphone-album-084_54473306120_o.jpg"

result = subprocess.run(
    ["exiftool", "-Description", "-s3", photo],
    capture_output=True, text=True
)
print(repr(result.stdout.strip()))