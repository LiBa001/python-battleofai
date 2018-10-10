from setuptools import setup, find_packages
import re


with open('battleofai/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='battleofai',
    version=version,
    description='A library for the battleofai API.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/LiBa001/python-battleofai',
    author='Linus Bartsch',
    author_email='linus.pypi@mabasoft.de',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    python_requires='>=3.6',
    keywords='wrapper library API AI python async',
    install_requires=['aiohttp'],
    packages=find_packages(exclude=['tests', 'examples', 'docs']),
    data_files=None,
    project_urls={
        'API': 'https://games.battleofai.net/api/',
        'Related project': 'https://github.com/TheMorpheus407/BattleOfAI'
    }
)
