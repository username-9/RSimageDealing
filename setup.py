from setuptools import setup

setup(
    name='UtilitiesForProcessingImage',
    version='0.0.1',
    packages=['UtilitiesForProcessingImage','UtilitiesForProcessingImage.BasicUtility','UtilitiesForProcessingImage.Statistic',
              'UtilitiesForProcessingImage.FurtherProcessing'],
    install_requires=['gdal',
                      'numpy',
                      'openpyxl',
                      ],
    author='username-9',
    author_email='escape_master@outlook.com',
    url='https://github.com/username-9/RSimageProcessing/UtilitiesForProcessingImage',
)