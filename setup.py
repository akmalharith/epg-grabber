from setuptools import setup, find_packages

setup(
    name="epg_grabber",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "requests==2.25.1",
        "pytz==2021.1",
        "beautifulsoup4==4.9.3",
        "xmltodict==0.12.0",
        "python-dotenv==0.19.2",
        "xmlunittest==0.5.0"
    ]
)