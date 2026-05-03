from setuptools import setup, find_packages

setup(
    name="tilebench",
    version="0.6.0",
    description="TileBench TUI — SemiCoLab unified interface for VeriFlow and TileWizard",
    author="Roman Lugo",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "tilebench": [
            "tui/themes.json",
            "tui/phrases.json",
        ],
    },
    install_requires=[
        "pyyaml",
        "rich>=13.0",
        "pyfiglet>=1.0",
        "textual>=0.60",
    ],
    entry_points={
        "console_scripts": [
            "tilebench=tilebench.tui.selector:run_selector",
        ],
    },
    python_requires=">=3.10",
)
