from setuptools import setup

setup(name='vnovel_tut',
      version='0.1',
      description='Pycon KR 2018 Tutorial - Make a simple programming language for visual novel',
      url='http://github.com/ipkn/vnovel_tut',
      author='Jaeseung Ha',
      author_email='ipknahama@gmail.com',
      license='GPL',
      packages=['vnovel_tut'],
      install_requires=[
          'pygments',
          'ply',
          'parsimonious',
      ],
      zip_safe=False)
