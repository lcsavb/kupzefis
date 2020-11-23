from setuptools import setup

setup(
    name='kupzefis',
    version='0.1',
    py_modules=['kupzefis'],
    install_requires=[
        'Click',
        'tqdm'
    ],
    entry_points='''
        [console_scripts]
        kupzefis=kupzefis:install
    '''
)