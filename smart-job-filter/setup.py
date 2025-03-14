#Sure, here's the contents for the file `/smart-job-filter/smart-job-filter/setup.py`:

from setuptools import setup, find_packages

setup(
    name='smart-job-filter',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'beautifulsoup4',
        'torch',
        'numpy',
        'pandas',
        'scikit-learn',
        'streamlit',
        'selenium'
    ],
    entry_points={
        'console_scripts': [
            'smart-job-filter=main:main',
        ],
    },
)