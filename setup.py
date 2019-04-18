from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="open-image-tools",
    version='0.0.1',
    author="Braincreators B.V",
    author_email="miguel@braincreators.com",
    description="Data processing tools for the Open Images Dataset",
    url="https://github.com/braincreators/open-images-tools",
    packages=find_packages(),
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
