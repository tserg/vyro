from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


extras_require = {
    "test": [
        "pytest>=7.1.2",
        "pytest-order>=1.0.1",
        "eth-ape==0.5.1",
        "ape-vyper==0.5.0",
        "ape-starknet==0.5.0a1",
        "ape-cairo==0.5.0a1",
    ],
    "lint": ["black==22.6.0", "flake8==4.0.1", "isort==5.10.1", "mypy==0.961"],
    "dev": ["pre-commit"],
}

extras_require["dev"] = extras_require["test"] + extras_require["lint"] + extras_require["dev"]

setup(
    name="vyro",
    version="0.1.0",
    description="Experimental Vyper to Cairo transpiler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gary Tse",
    author_email="",
    url="https://github.com/tserg/vyro",
    keywords=["ethereum", "starknet", "vyper", "cairo", "transpiler"],
    python_requires=">=3.9,<3.10",
    packages=find_packages(where=".", include=["vyro*"]),
    install_requires=["vyper==0.3.7", "cairo-lang==0.10.0"],
    extras_require=extras_require,
    entry_points={"console_scripts": ["vyro=vyro._cli.__main__:main"]},
)
