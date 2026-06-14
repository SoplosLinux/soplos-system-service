from setuptools import setup, find_packages

setup(
    name='soplos-system-services',
    version='1.0.0-1',
    description='GTK3 graphical manager for systemd services on Soplos Linux',
    author='Sergi Perich',
    author_email='info@soploslinux.com',
    url='https://github.com/SoplosLinux/soplos-system-service',
    license='GPL-3.0+',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=['PyGObject'],
    entry_points={
        'gui_scripts': [
            'soplos-system-services = main:main',
        ]
    },
)
