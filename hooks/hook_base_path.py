import os
import sys


if getattr(sys, "frozen", False):
    os.environ["APP_BASE_PATH"] = getattr(sys, "_MEIPASS", os.getcwd())
else:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.environ["APP_BASE_PATH"] = project_root

