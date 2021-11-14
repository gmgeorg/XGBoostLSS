from setuptools import setup, find_packages

setup(
    name="xgboostlss",
    version="0.1.0",
    description="XGBoostLSS - An extension of XGBoost to probabilistic forecasting",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Alexander März",
    author_email="alex.maerz@gmx.net",
    url="https://github.com/StatMixedML/XGBoostLSS",
    license="Apache License 2.0",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    package_data={'': ['datasets/*.csv']},
    zip_safe=True,
    python_requires=">=3.7",
    install_requires=[
        "xgboost>=1.4.2",
        "optuna>=2.9.1",
        "scikit-learn>=0.24.2",
        "shap>=0.39.0",
        "numpy~=1.16",
        "pandas~=1.1",
        "plotnine>=0.8.0",
        "scipy",
        "tqdm",
        "matplotlib",
        "pkg_resources",
    ],
    test_suite="tests",
    tests_require=["flake8", "pytest"],
)
