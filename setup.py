from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


extras_require = {
    "test": [
        "pytest>=7.1.2",
        "pytest-order>=1.0.1",
        "eth-ape==0.4.4",
        "ape-vyper==0.4.0",
        "ape-starknet==0.4.0a1",
        "ape-cairo==0.4.0a0",
    ],
    "lint": ["black==22.6.0", "flake8==4.0.1", "isort==5.10.1", "mypy==0.961"],
}

extras_require["dev"] = extras_require["test"] + extras_require["lint"]

setup(
    name="vyro",
    version="0.0.1",
    description="Experimental Vyper to Cairo transpiler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gary Tse",
    author_email="",
    url="https://github.com/tserg/vyro",
    keywords=["ethereum", "starknet", "vyper", "cairo", "transpiler"],
    python_requires=">=3.7,<3.10",
    packages=find_packages(where=".", include=["vyro*"]),
    install_requires=["vyper==0.3.6", "cairo-lang==0.9.1"],
    extras_require=extras_require,
    entry_points={"console_scripts": ["vyro=vyro._cli.__main__:main"]},
)
