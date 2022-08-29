import setuptools

setuptools.setup(
    name='zhutils',
    version='0.1.2',
    description='A personal collection of tools for data processing',
    author='Mikhail Zharkov',
    author_email='mzharkov@sfu-kras.ru',
    url='https://github.com/mikewellmeansme/ZhUtils',
    packages=setuptools.find_packages(),
    python_requires='>=3.7, <4',
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'pandera'
    ]
)
