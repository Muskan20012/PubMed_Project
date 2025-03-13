# PubMed Query Project

## Overview

This project provides tools to query PubMed articles using flexible search terms. It fetches, filters, and parses PubMed data, making it easier to extract relevant scientific publications. Additionally, ChatGPT was utilized for guidance during the development process.

---

## Code Organization

The project is organized as follows:

```
pubmed/
│
├── src/
│   ├── pubmed/         # Contains core logic (API interactions, parsing)
│   │   ├── api.py      # Functions to interact with PubMed API
│   │   ├── cli.py    # CLI for query
│   
│
├── tests/              # Unit tests for the project
│
├── .env                # Environment variables (API keys, Base URLs)
├── pyproject.toml      # Project metadata and dependency management
├── README.md           # Project documentation
├── poetry.lock         # Poetry lock file for dependencies
```

---

## Installation

1. **Clone the Repository**  
   ```bash
   git clone <repository_url>
   cd PubMed_project
   ```

2. **Set Up Environment Variables**  
   Create a `.env` file in the root directory and add the following:
   ```plaintext
   API_KEY=<your_pubmed_api_key>
   API_URL=https://eutils.ncbi.nlm.nih.gov/entrez/eutils
   ```

3. **Install Dependencies**  
   Install Poetry if not already installed:
   ```bash
   pip install poetry
   ```
   Then, install project dependencies:
   ```bash
   poetry install
   ```

4. **Activate the Virtual Environment**  
   ```bash
   poetry shell
   ```

---

## Usage

Run the CLI to query PubMed articles:
```bash
poetry run get-papers-list -q "<search_query>" -n <number_of_results>
```

### Example:
```bash
poetry run get-papers-list -q "cancer AND gene therapy[TI]" -n 10
```

### Command-Line Options:
- `-q` or `--query`: Specify the search query.
- `-n` or `--number`: Number of results to fetch (default: 10).

---

## Tools and Libraries Used

1. **Python Libraries**  
   - **httpx**: For asynchronous HTTP requests ([httpx documentation](https://www.python-httpx.org/)).
   - **lxml**: For parsing XML data ([lxml documentation](https://lxml.de/)).
   - **dotenv**: For environment variable management ([python-dotenv](https://pypi.org/project/python-dotenv/)).
   - **Poetry**: For dependency and project management ([Poetry documentation](https://python-poetry.org/)).
   - **Typing**: For type hints and better code readability.

2. **PubMed API**  
   - The project uses PubMed's Entrez Programming Utilities (E-utilities) ([PubMed E-utilities Documentation](https://www.ncbi.nlm.nih.gov/books/NBK25500/)).

3. **ChatGPT**  
   - ChatGPT, a large language model, was used for generating code suggestions, debugging, and providing structured development insights during the project. ([ChatGPT Information](https://openai.com/chatgpt))

---

## Testing

Run the tests to ensure everything is working as expected:
```bash
poetry run pytest tests/
```

---

## Contributing

Feel free to fork the repository and create a pull request with your enhancements or fixes.

