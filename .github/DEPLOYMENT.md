# Deployment Guide

This project uses GitHub Actions to automatically publish to PyPI. Here's how to set it up:

## Setup Instructions

### Option A: Trusted Publishing (Recommended - More Secure)

1. Go to [PyPI Project Settings](https://pypi.org/manage/project/contraction-fix/settings/)
2. Scroll to "Trusted publishing" section
3. Click "Add a new publisher"
4. Fill in:
   - **Owner**: `xga0` (your GitHub username)
   - **Repository name**: `contraction_fix`
   - **Workflow name**: `publish.yml`
   - **Environment name**: (leave empty)
5. Click "Add"

### Option B: API Token (Fallback Method)

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Scroll down to "API tokens" section
3. Click "Add API token"
4. Give it a name (e.g., "GitHub Actions - contraction-fix")
5. Set scope to "Entire account" or specific to your project
6. Copy the token (starts with `pypi-`)

### 2. Add Token to GitHub Secrets (Only needed for Option B)

1. Go to your GitHub repository
2. Click on "Settings" tab
3. Go to "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Name: `PYPI_API_TOKEN`
6. Value: Paste your PyPI API token
7. Click "Add secret"

## Deployment Options

### Option 1: GitHub Releases (Recommended)
- Create a release on GitHub
- The workflow will automatically trigger and publish to PyPI
- Use semantic versioning (e.g., v0.2.1, v1.0.0)

### Option 2: Version Tags
- Create and push a version tag: `git tag v0.2.1 && git push origin v0.2.1`
- The manual workflow will trigger automatically

### Option 3: Manual Trigger
- Go to Actions tab in your GitHub repository
- Select "Publish to PyPI (Manual/Tag)" workflow
- Click "Run workflow"

## Features

### ✅ **Automated Testing**
- Tests run on Python 3.8-3.12 before publishing
- Prevents publishing broken packages
- Can be skipped for manual workflow if needed

### ✅ **Version Validation**
- Automatically checks if version already exists on PyPI
- Prevents accidental duplicate publishing
- Shows clear error messages

### ✅ **Dual Publishing Methods**
- Tries trusted publishing first (more secure)
- Falls back to API token if trusted publishing fails
- Supports both methods seamlessly

### ✅ **Package Validation**
- Validates package structure before publishing
- Checks metadata and distribution files
- Ensures PyPI compatibility

## Important Notes

- **Always update the version in `setup.py` before publishing**
- The workflows automatically prevent duplicate version publishing
- Tests run on all supported Python versions (3.8-3.12)
- Package validation occurs before every publish
- Trusted publishing is more secure than API tokens

## Version Update Process

1. Update version in `setup.py` (e.g., from `0.2.0` to `0.2.1`)
2. Commit changes: `git add setup.py && git commit -m "Bump version to 0.2.1"`
3. Push to GitHub: `git push origin main`
4. Create a release or tag (depending on your preferred method)
5. GitHub Actions will:
   - Run tests on all Python versions (3.8-3.12)
   - Validate the package
   - Check for duplicate versions
   - Publish to PyPI automatically

## Troubleshooting

### "Version already exists" error
- Update the version number in `setup.py`
- Current PyPI version: Check https://pypi.org/project/contraction-fix/

### Tests failing
- Run tests locally: `python -m pytest tests/ -v`
- Fix any issues before publishing
- Or use manual workflow with "Skip tests" option (not recommended)

### Publishing fails
- Check GitHub Actions logs for detailed error messages
- Verify PyPI credentials are set up correctly
- Ensure package builds successfully: `python -m build` 