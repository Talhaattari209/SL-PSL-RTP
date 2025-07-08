from setuptools import setup, find_packages
import os

setup(
    name="sign_language_translator",
    version="1.0.0",
    description="Sign Language Translator - Pakistan Sign Language and American Sign Language Translation",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(include=["sign_language_translator*"]),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.28.0",
        "tqdm",
        "scipy",
        "scikit-learn",
        "torch",
        "torchvision",
        "opencv-python",
        "numpy",
        "requests",
        "click",
        "pillow",
        "matplotlib",
        "mediapipe",
        "tensorflow",
        "transformers",
        "deep_translator==1.11.4",
    ],
    python_requires=">=3.9,<3.14",
    package_data={
        "": ["*.txt", "*.json", "*.yaml", "*.yml"],
    },
    data_files=[
        ("sign_language_translator/config", ["sign_language_translator/config/urls.json"]),
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 