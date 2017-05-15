import codecs
from setuptools import setup, find_packages

entry_points = {
    "z3c.autoinclude.plugin": [
        'target = nti.app',
    ],
}


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.app.contentlibrary_store',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI Contentlibrary store",
    long_description=(_read('README.rst') + '\n\n' + _read("CHANGES.rst")),
    license='Apache',
    keywords='pyramid store content library',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti', 'app'],
    install_requires=[
        'setuptools',
        'nti.store',
        'nti.contentlibrary',
    ],
    entry_points=entry_points,
    test_suite="nti.app.contentlibrary_store.tests",
)
