from setuptools import setup


setup(
    name='treasurydotgovyc',
    description='Yield curve from treasury.gov daily publication',
    packages=['treasurydotgovyc'],
    url='https://github.com/jordanhitchcock/cred',
    author='Jordan Hitchcock',
    license='MIT',
    python_requires='>=3.7',
    install_requires=['requests', 'lxml', 'python-dateutil', 'numpy'],
)
