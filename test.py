import os

global_images_path = os.path.join(os.path.expanduser("~"), "ChickenBrothers")

print(global_images_path)

pa = os.path.join(os.path.dirname(os.path.abspath(__file__)),"src","public")
print(pa)