from setuptools import setup, find_packages

setup(
    name="koshatrack",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'numpy',
        'scipy',
        'sgp4',
        'astropy',
        'requests',
        'pytest',
    ],
    python_requires='>=3.8',
)
