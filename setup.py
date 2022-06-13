import setuptools
import pathlib
import pkg_resources

with pathlib.Path('requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]

setuptools.setup(
    name='zh_utils',
    version='0.0.1',
    description='A personal collection of tools for data processing',
    author='Mikhail Zharkov',
    author_email='mzharkov@sfu-kras.ru',
    url='https://github.com/mikewellmeansme/ZhUtils',
    packages=setuptools.find_packages(),
    install_requires=install_requires
)
