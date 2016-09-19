from setuptools import setup

setup(
    name='docker-compose-watch',
    version='0.0.1',
    description='A watcher for docker compose',
    url='http://github.com/hnovikov/docker-compose-watch',
    author='Hrant Novikov',
    author_email='hrant.novikov@gmail.com',
    license='MIT',
    install_requires=['watchdog'],
    packages=['dockercomposewatch'],
    entry_points={
        'console_scripts': [
            'docker-compose-watch=dockercomposewatch:main',
        ],
    }
)
