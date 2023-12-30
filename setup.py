from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='prometheus-tstick-exporter',
    packages=['tstick_exporter'],
    version='0.0.1',
    long_description=long_description,
    long_description_content_type="text/markdown",
    description='Prometheus exporter for the tstick',
    keywords=['prometheus', 'tstick'],
    classifiers=[],
    python_requires='>=3',
    install_requires=['attrdict==2.0.1', 'prometheus_client==0.19.0 ', 'requests==2.31.0', 'python-json-logger==2.0.7', 'python-osc==1.8.3'],
    entry_points={
        'console_scripts': [
            'tstick_exporter=tstick_exporter.exporter:main',
        ]
    }
)
