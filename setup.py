from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="malvryx-av",
    version="1.0.0",
    author="Malvryx",
    author_email="malvryx@proton.me",
    description="Next-Generation Antivirus Engine with Real-Time Protection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/malvryx/malvryx-av",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yara-python>=4.3.0",
        "psutil>=5.9.0",
        "watchdog>=3.0.0",
        "flask>=2.3.0",
        "flask-socketio>=5.3.0",
        "eventlet>=0.33.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "malvryx=src.main:main",
        ],
    },
)
