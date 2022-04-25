import setuptools

setuptools.setup(
    name="chessenv",
    packages=["chessenv"],
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["build.py:ffibuilder"],
    install_requires=["cffi>=1.0.0"],
)
