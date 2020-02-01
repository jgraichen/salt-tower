import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="salt-tower",
    version="1.2.0",
    author="Jan Graichen",
    author_email="jgraichen@altimos.de",
    description="A Flexible External Salt Pillar Module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jgraichen/salt-tower",
    packages=setuptools.find_packages(include=["salt_tower", "salt_tower.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Systems Administration",
    ],
    entry_points='''
        [salt.loader]
        pillar_dirs = salt_tower.loader:pillar_dirs
        render_dirs = salt_tower.loader:renderers_dirs
    ''',
)
