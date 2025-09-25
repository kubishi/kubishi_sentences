from setuptools import setup, find_packages

setup(
    name='yaduha',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'python-dotenv',
        'openai',
        'spacy',
        'tqdm',
        'torch',
        'torchvision',
        'torchaudio',
        'transformers',
        'sentence-transformers',
        'pydantic',
        'requests',
        'pytest',
    ],
    dependency_links=[
        'https://download.pytorch.org/whl/cpu'  # The custom index URL for the CPU wheels
    ],
)