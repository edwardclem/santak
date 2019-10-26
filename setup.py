import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="santak",
    version="0.1",
    python_requires=">=3",
    author="Edward Williams",
    author_email="eddiecwilliams@gmail.com",
    description="Shape context matching of cuneiform characters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edwardclem/santak",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=["scikit-learn", "numpy", "matplotlib", "tqdm", "luigi"],
)
