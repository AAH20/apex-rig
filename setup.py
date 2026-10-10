from setuptools import setup, find_packages

setup(
    name="apex-rig",
    version="1.0.0",
    description="Sovereign Multi-Harness Aggregator, Hardware-Aware Cognitive Router & Agent Mesh",
    author="Ahmed Hassan",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "apexrig = apex_rig.cli:main",
        ],
    },
    python_requires=">=3.9",
)
