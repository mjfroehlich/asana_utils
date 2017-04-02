try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'asana_utils',
    'author': 'Martin Froehlich',
    'version': '0.1',
    'entry_points': {
        'console_scripts': [
            'asana_meta_from_name = asana_utils:meta_from_name']},
    'install_requires': [
        'asana'
    ],
    'py_modules': ['asana_utils'],
    'test_suite': 'asana_utils'
}

setup(**config)
