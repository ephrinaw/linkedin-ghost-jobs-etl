# Contributing to LinkedIn Ghost Jobs ETL Pipeline

Thank you for your interest in contributing to this project! This guide will help you get started.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic understanding of ETL pipelines and data analysis

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/linkedin-ghost-jobs-etl.git
   cd linkedin-ghost-jobs-etl
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 standards
- Use type hints where applicable
- Write descriptive docstrings
- Keep functions focused and small

### Testing
- Write tests for all new features
- Maintain >90% test coverage
- Use pytest for testing framework
- Include both unit and integration tests

### Commit Messages
Use conventional commit format:
```
feat: add new ghost job detection rule
fix: resolve database connection issue
docs: update API documentation
test: add tests for Finnish analyzer
```

## 🎯 Areas for Contribution

### High Priority
- [ ] Additional job board integrations
- [ ] Machine learning detection models
- [ ] Performance optimizations
- [ ] Documentation improvements

### Medium Priority
- [ ] New visualization types
- [ ] Additional country-specific analyzers
- [ ] API rate limiting improvements
- [ ] Docker optimization

### Low Priority
- [ ] UI/Web interface
- [ ] Mobile app integration
- [ ] Advanced reporting features

## 📝 Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following our guidelines
   - Add/update tests
   - Update documentation

3. **Test Your Changes**
   ```bash
   pytest tests/ -v
   flake8 src/ tests/
   black src/ tests/
   ```

4. **Submit Pull Request**
   - Provide clear description
   - Reference related issues
   - Include screenshots if applicable

## 🐛 Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

## 💡 Feature Requests

For new features, please:
- Check existing issues first
- Provide clear use case
- Explain expected behavior
- Consider implementation complexity

## 📞 Getting Help

- **Issues**: Use GitHub issues for bugs and features
- **Discussions**: Use GitHub discussions for questions
- **Email**: Contact maintainers for sensitive issues

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to making job searching more transparent!