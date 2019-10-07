from setuptools import setup

VERSION = "0.0.1dev0"

setup(
    name='cellphone-recharge-predictor',
    version=VERSION,
    description='Cellphone Recharge predictor',
    author='FDA Dev Team',
    author_email='',
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],
    packages=['mpi', 'shared', 'etl', 'training'],
    install_requires=[
        'scikit-learn',
        'pandas',
    ],
)
