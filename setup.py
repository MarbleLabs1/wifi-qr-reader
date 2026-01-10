from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wifi-qr-reader",
    version="1.0.0",
    author="marbleceo",
    author_email="marbleceo@github.com",
    description="Leitor de QR Code de WiFi com visualização da câmera em tempo real",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MarbleCeo/wifi-qr-reader",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.6.0",
        "PyQt5>=5.15.0",
        "pyzbar>=0.1.9",
    ],
    entry_points={
        "console_scripts": [
            "wifi-qr-reader=wifi_qr_reader:main",
        ],
    },
    keywords="wifi qr code scanner network camera",
    project_urls={
        "Bug Reports": "https://github.com/MarbleCeo/wifi-qr-reader/issues",
        "Source": "https://github.com/MarbleCeo/wifi-qr-reader",
    },
)
