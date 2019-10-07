from setuptools import setup

VERSION = "0.0.1dev0"

setup(
    name='ml-forecasting',
    version=VERSION,
    description='Forecasting Item Sales',
    author='Machine Learning Team',
    author_email='',
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],
    packages=['mpi', 'ml_forecasting', 'etl', 'training'],
    install_requires=[
        'scikit-learn',
        'pandas',
    ],
    extras_require={
        'dev': [
            'pep8',
            'flake8',
            'black'
        ]
    },

)
