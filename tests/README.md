# Tests

This directory contains the test suite for the Mergington High School Activities API.

## Running Tests

To run all tests:
```bash
python -m pytest tests/ -v
```

To run tests with coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

To run a specific test class:
```bash
python -m pytest tests/test_activities.py::TestActivitySignup -v
```

## Test Structure

- `conftest.py` - Contains fixtures and test configuration
- `test_activities.py` - Contains all API endpoint tests

## Test Categories

### TestBasicEndpoints
Tests for basic API functionality:
- Root endpoint redirect
- Getting all activities

### TestActivitySignup  
Tests for student signup functionality:
- Successful signup
- Duplicate signup prevention
- Non-existent activity handling
- URL encoding handling

### TestActivityUnregister
Tests for student unregistration functionality:
- Successful unregistration
- Error handling for various edge cases
- URL encoding handling

### TestCompleteWorkflow
End-to-end integration tests:
- Complete signup/unregister workflows
- Multiple participant management

### TestDataValidation
Data integrity and validation tests:
- Required fields validation
- Data type validation
- Activity name consistency

## Test Coverage

The test suite provides 100% code coverage for the API endpoints.