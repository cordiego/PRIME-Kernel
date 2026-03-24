from setuptools import setup, find_packages

setup(
    name="prime-kernel",
    version="1.0.0",
    author="Diego Córdoba Urrutia",
    author_email="diego@primenergeia.com",
    description="PRIME-Kernel — Shared core library for PRIMEnergeia SBUs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cordiego/PRIME-Kernel",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21",
    ],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
