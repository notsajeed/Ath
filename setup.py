from setuptools import setup, find_packages

setup(
    name="ath",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ath=ath.cli:app",
        ],
    },
    python_requires=">=3.8",
    author="sajeed",
    description="Your personal, per-folder AI assistant",
)