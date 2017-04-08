from setuptools import setup, find_packages

setup(name='artip',
      version='1.0',
      install_requires=[
          'coloredlogs',
          'pyyaml',
          'pybuilder'
      ],
      scripts=['build.py'],
      packages=find_packages('src/main'),  # include all packages under src
      package_dir={'': 'src/main'},  # tell distutils packages are under src
      entry_points={
          'console_scripts': [
              'artip = build:run',
          ]
      },
      include_package_data=True,

      author="ThoughtWorks",
      author_email="iucaa@thoughtworks.com",
      description="This is an automation pipeline for generating radio telescope images",
      license="IUCAA",
      platforms="Python"
      )
