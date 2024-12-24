# Turnitin PoC

### Overview
**Turnitin PoC** is a proof of concept on the text obfuscation technique to analyze and challenge the detection systems like Turnitin. The project shows various lexical, structural, and complexity-based changes in the text and allows the user to learn concepts regarding NLP.

---

## Features
- **Lexical Alteration**: Modify word usage and phrasing to obfuscate text.
- **Structural Alteration**: Rearrange sentences or paragraphs to make detection more challenging.
- **Complexity Alteration**: Adjust text depth and layers (e.g., using synonyms, sentence complexity changes).

---

## Technologies Used
- **Python 3.13.1**
- **Libraries**: 
  - `docx` (for handling Word document processing)
  - `random` (for randomized variations)
  - Any other dependencies mentioned in the `requirements.txt` file.

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/turnitin-poc.git
   cd turnitin-poc
   ```
   
2. **Set up a Virtual Environment:**
   ```bash
   python -m venv env
   source env/bin/activate     # On Linux/Mac
   env\Scripts\activate        # On Windows
   ```
   
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Ensure packages like `nltk` are installed.

4. **Run the Project:**
   ```bash
   python main.py
   ```

---

## Usage
1. Provide an input sentence or paragraph.
2. Apply the obfuscation techniques (lexical, structural, or complexity changes).
3. Output the altered text and analyze its compatibility with detection systems.
   
Here is an example:
```python
Input:   "This is a test sentence to explore detection techniques."
Output:  "This happens to be a trial statement, researching methods of recognition."
```

---

## Contribution Guidelines
Contributions are welcome! To contribute:
1. Fork the project and create a branch.
2. Make your changes.
3. Submit a pull request describing your updates.

---

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for more details.
