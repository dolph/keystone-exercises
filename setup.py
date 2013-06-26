import setuptools


setuptools.setup(
    name='keystone-workout',
    version='0.1.0',
    description='Exercise keystone using python-keystoneclient',
    author='Dolph Mathews',
    author_email='dolph.mathews@gmail.com',
    url='http://github.com/dolph/keystone-workout',
    install_requires=[
        'python-keystoneclient'],
    entry_points={
        'console_scripts': [
            'keystone-workout = keystoneworkout.cli:cli']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP'
        'Topic :: Utilities',
    ],
)
