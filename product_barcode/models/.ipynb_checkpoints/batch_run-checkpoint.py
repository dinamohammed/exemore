# -*- coding: utf-8 -*-

from subprocess import Popen
import os
os.system("/src/user/product_barcode/ZippraPrint.bat")

p = Popen("ZippraPrint.bat", cwd=r"/src/user/product_barcode")
# p = Popen("ZippraPrint.bat", cwd=r"C:\Users\Nabil\Desktop")
stdout, stderr = p.communicate()
