# Contributing to the Project

Thank you for considering contributing to this project! We welcome contributions of all kinds, including bug reports, feature requests, documentation improvements, and code contributions. This guide provides information on how to contribute to the project effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [How to Contribute](#how-to-contribute)
   - [Reporting Issues](#reporting-issues)
   - [Requesting Features](#requesting-features)
   - [Resolving Issues](#resolving-issues)
3. [Code Guidelines](#code-guidelines)
4. [Setting Up the Development Environment](#setting-up-the-development-environment)
5. [Constributor License Agreement(CLA)](#Contributor-License-Agreement-(CLA))
6. [Code of Conduct](#code-of-conduct)

## Getting Started

To get started with contributing, first, make sure you have a GitHub account. Then, fork the repository and clone it to your local machine.

```bash
git clone https://github.com/YOUR_USERNAME/PROJECT_NAME.git
cd PROJECT_NAME
```
Replace ```YOUR_USERNAME``` with your GitHub username and ```PROJECT_NAME``` with the name of the repository.
## How to Contribute
### Reporting Issues
If you find any bugs or have any suggestions, please create an [issue](https://github.com/BrandonS09/SearchVision/issues) on GitHub. When reporting an issue, please include:

- A clear and descriptive title.
- A detailed description of the problem, including steps to reproduce.
- Any relevant screenshots or error messages.
- Your development environment (e.g., operating system, Python version).

### Requesting Features
To request a new feature, please open a [feature request](https://github.com/BrandonS09/SearchVision/issues) on GitHub. Describe your proposed feature in detail, including:

- The problem or use case your feature addresses.
- Any ideas for how it could be implemented.
- Potential alternatives or workarounds.

### Resolving Issues
When resolving issues, please make sure it has the ```help wanted``` label and isn't already taken. To resolve an issue, you need to submit a pull request. To submit a pull request(PR), follow these steps:
1. Fork the repository to your Github account
2. Create a new branch for your feature or bug fix
```
git checkout -b feature/your-feature-name
```
3. Make your changes in the new branch.
4. Commit your changes with a clear and descriptive commit message:
```
git commit -m "Add: Detailed description of the change"
```
6. Push your changes to your fork
```
git push origin feature/your-feature-name
```
7. Submit a pull request to the ```main``` branch of the original repository. Make sure to include a clear description of your changes and the purpose of the PR.

## Code Guidelines
To ensure a consistent and high-quality codebase, please follow these guidelines:

- Code Style: Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Type Annotations: Use Python type annotations to specify function arguments and return types.
- Error Handling: Ensure that all code is robust and handles errors gracefully.
- Testing: Write unit tests for new features and bug fixes.
- Documentation: Document your code with clear comments and update any relevant documentation (e.g., README.md, docstrings).

## Setting Up the Development Environment
To set up the development environment, follow these steps:
1. Clone the repository
```
git clone https://github.com/YOUR_USERNAME/PROJECT_NAME.git
cd PROJECT_NAME
```
2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Happy Coding!

## Contributor License Agreement (CLA)

Before we can accept your contributions, you will need to sign a Contributor License Agreement (CLA). This agreement ensures that you are eligible to contribute to this project and that your contributions can be freely used and redistributed under the terms of the AGPL license.

### How to Sign the CLA

1. **Read the CLA**: You can find the Contributor License Agreement [here](LINK_TO_CLA_DOCUMENT). Please read it carefully to understand the terms.
2. **Sign the CLA**: To sign the CLA, you can:
   - **Electronically Sign**: Complete the electronic signature process [here](LINK_TO_ELECTRONIC_SIGNATURE_FORM).
   - **Email a Signed Copy**: Download the CLA, sign it, and send it via email to [your-email@example.com](mailto:your-email@example.com).

### Why Do We Need a CLA?

The CLA helps us ensure that the intellectual property rights for the contributions are clearly defined, allowing us to maintain the project under the AGPL license. This protects both you as a contributor and us as the project maintainers.

### Important Notes

- You need to sign the CLA only once; after that, you can contribute as much as you want without re-signing.
- If you are contributing on behalf of your employer, make sure they are aware of and approve of your contributions under the terms of the CLA and AGPL license.

Thank you for your understanding and cooperation!


## Code of Conduct
We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Please read it to understand what actions will and will not be tolerated.

By contributing to this project, you agree to abide by its terms.

---
Thank you for your interest in contributing! We value and appreciate your input and efforts in making this project better.
