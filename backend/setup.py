from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="financeflareai-backend",
    version="1.0.0",
    author="FinanceFlareAI Team",
    author_email="team@financeflareai.com",
    description="AI-powered personal budget tracker backend API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/financeflareai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "financeflareai=app.main:main",
        ],
    },
) 