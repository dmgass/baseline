from setuptools import setup

LONG_DESCRIPTION = """
""".lstrip()

setup(
    name='baseline',
    version='0.1.0',
    description='Ease maintenance baselined text.',
    long_description=LONG_DESCRIPTION,
    classifiers=[
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Topic :: Text Processing',
    ],
    keywords='test',
    url='https://github.com/dmgass/baseline',
    author='Daniel Mark Gass',
    author_email='dan.gass@gmail.com',
    license='MIT',
    packages=['baseline'],
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points={
        'console_scripts': ['baseline=baseline.__main__:main'],
    }
)
