from setuptools import setup, find_packages


version = "0.5"

setup(
    name='gencharts',
    packages=find_packages(),
    version=version,
    description='Generate html charts with Altair',
    author='synw',
    author_email='synwe@yahoo.com',
    url='https://github.com/synw/gencharts',
    download_url='https://github.com/synw/gencharts/releases/tag/' + version,
    keywords=['errors', "error_handling"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    zip_safe=False,
    install_requires=[
        'altair'
    ],
)
