from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


extras_require = {
    "lint": [
        "black==22.6.0",
        "flake8==4.0.1",
        "isort==5.10.1",
        "mypy==0.961",
    ]
}

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
    python_requires=">=3.7,<3.11",
    install_requires=[
        "vyper @ git+https://github.com/vyperlang/vyper@c3e43d7b8a2e2236e236b9f23c3a8f9a96de349c",
        "cairo-lang==0.9.0",
    ],
    extras_require=extras_require,
    entry_points={
        "console_scripts": ["vyro=vyro._cli.__main__:main"],
    }
)
