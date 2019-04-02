import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pytrendsdaily',
    version='1.0.0',
    description='Fetches Daily Data from Google Trends.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/salompas/pytrendsdaily',
    author='Guilherme Salome',
    author_email='guilhermesalome@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha", ],
    install_requires=[
        "pandas >= 0.23.0",
        "pytrends >= 4.4.0",
    ],
)
