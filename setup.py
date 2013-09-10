from distutils.core import setup


setup(
    name='helio',
    version='1.0b1',
    py_modules=['helio'],
    requires=[
        'coverage',
        'mock',
        'nose',
        'wsgiref',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Helio',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)