from setuptools import setup, find_packages

setup(
    name="soplos-system-services",
    version="0.1.0",
    description="Gestor gráfico de servicios SystemD para Soplos Linux",
    author="Sergi Perich",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["PyGObject"],
    entry_points={
        "gui_scripts": [
            "soplos-system-services = main:main"
        ]
    },
)
