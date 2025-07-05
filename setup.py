from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A comprehensive SNMP parser package for Python"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="snmpwalk-parser",
    version="1.0.0",
    packages=find_packages(),
    author="Kunal Raut",
    author_email="kunalraut489@gmail.com",
    description="A comprehensive SNMP parser package for extracting and analyzing SNMP walk data",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/kunalraut/snmpwalk-parser",  # Update with your repo URL
    license="MIT",
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    python_requires='>=3.7',
    install_requires=read_requirements(),
    
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
            'isort>=5.0',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=1.0',
        ],
        'examples': [
            'matplotlib>=3.0',
            'pandas>=1.0',
            'jupyter>=1.0',
        ]
    },
    
    entry_points={
        'console_scripts': [
            'snmpwalk-parser=snmpwalk_parser.cli:main',
        ],
    },
    
    project_urls={
        'Documentation': 'https://snmpwalk-parser.readthedocs.io/',
        'Source': 'https://github.com/kunalraut/snmpwalk-parser',
        'Tracker': 'https://github.com/kunalraut/snmpwalk-parser/issues',
    },
    
    keywords=[
        'snmp', 'snmpwalk', 'network', 'monitoring', 'parser', 
        'network-management', 'mib', 'oid', 'system-administration'
    ],
    
    include_package_data=True,
    package_data={
        'snmpwalk_parser': ['data/*.json', 'templates/*.txt'],
    },
    
    zip_safe=False,
)