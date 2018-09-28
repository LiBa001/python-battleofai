from setuptools import setup, find_packages

with open('Readme.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='battleofai',
    version='0.1.0',
    description='A wrapper for the battleofai API.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/LiBa001/python-battleofai',
    author='Linus Bartsch',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    python_requires='>=3.6',
    keywords='wrapper library API AI python',
    install_requires=['requests'],
    packages=find_packages(exclude=['tests', 'examples']),
    data_files=None,
    project_urls={
        'API': 'https://games.battleofai.net/api/',
        'Related project': 'https://github.com/TheMorpheus407/BattleOfAI'
    }
)
