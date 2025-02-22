from setuptools import setup, find_packages
import sys

# Define entry point for Windows and Unix-like systems
entry_point = "keepactive=src.keep_active_pro:main"

setup(
    name="KeepActivePro",
    version="1.0",
    description="A simple tool to keep your system awake and prevent sleep mode",
    author="Ravishankar Gavhane",
    author_email="gavhane.ravishankar4@gmail.com",
    url="https://github.com/yourusername/KeepActivePro",
    packages=find_packages(),
    install_requires=["pyautogui", "tk", "Pillow"],
    entry_points={
        "console_scripts": [
            entry_point,
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)