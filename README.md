# Boolean Expression Simplifier - Standalone Version

A complete boolean expression simplifier using the Karnaugh MAP logic with Python Flask backend and HTML/CSS/JS frontend.

## Features

- ✅ **Complements AFTER variables**: A' instead of 'A
- ✅ **Alphabetically sorted terms**: A'BC instead of BCA'
- ✅ Supports 2-4 variables (A, B, C, D)
- ✅ Sum of Products (SOP) mode
- ✅ Product of Sums (POS) mode
- ✅ Don't care term support
- ✅ Modern, responsive UI with circuit-board theme

## File Structure

```
standalone/
├── index.html          # Main HTML file
├── styles.css          # CSS styling
├── script.js           # Frontend JavaScript
├── app.py              # Flask backend server
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- A modern web browser

### Step 1: Install Python Dependencies

Open a terminal/command prompt in the `standalone` directory and run:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install Flask flask-cors
```

### Step 2: Start the Flask Backend

In the `standalone` directory, run:

```bash
python app.py
```

You should see:
```
🚀 Starting Boolean Simplifier API...
📡 Server running at http://localhost:5000
🔗 Open index.html in your browser to use the app
```

### Step 3: Open the Frontend

Simply open `index.html` in your web browser by:
- Double-clicking the file, OR
- Right-click → Open with → Your browser, OR
- Drag and drop into browser window

## Usage

1. **Select Number of Variables** (2-4)
2. **Choose Mode** (SOP or POS)
3. **Enter Terms** as comma-separated numbers (e.g., `0, 1, 3, 7`)
4. **Optional**: Add don't care terms
5. **Click** "Simplify Expression"
6. **View** the simplified boolean expression!

## Examples

### Example 1: Sum of Products (SOP)
- Variables: 3 (A, B, C)
- Minterms: `0, 1, 3, 7`
- Result: `A'B + BC`

### Example 2: With Don't Cares
- Variables: 4 (A, B, C, D)
- Minterms: `0, 2, 5, 7, 8, 10, 13, 15`
- Don't Cares: `1, 3, 9, 11`
- Result: Simplified expression

### Example 3: Product of Sums (POS)
- Variables: 3 (A, B, C)
- Mode: POS
- Maxterms: `0, 3, 5, 6`
- Result: POS expression

## API Endpoints

### POST /simplify
Simplify a boolean expression

**Request Body:**
```json
{
  "minterms": [0, 1, 3, 7],
  "num_vars": 3,
  "mode": "SOP",
  "dont_cares": [2]
}
```

**Response:**
```json
{
  "simplified": "A'B + BC",
  "variables": ["A", "B", "C"],
  "original_terms": [0, 1, 3, 7],
  "dont_cares": [2],
  "mode": "SOP"
}
```

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "Boolean Simplifier API is running"
}
```

## Algorithm Details

This implementation uses the **Karnaugh MAP logic**:

1. Convert minterms to binary representation
2. Group terms by number of 1s
3. Combine terms differing by one bit
4. Mark combined terms as used
5. Repeat until no more combinations possible
6. Unused terms become prime implicants
7. Convert prime implicants to boolean expressions
8. Sort variables alphabetically with complements after

## Formatting Rules

- **Complements**: Always after the variable (A', B', C', D')
- **Alphabetical order**: Terms sorted alphabetically (A before B, etc.)
- **SOP format**: Terms joined with ` + ` (e.g., `A'B + BC`)
- **POS format**: Terms in parentheses with ` · ` (e.g., `(A + B') · (C' + D)`)

## Troubleshooting

### Backend won't start
- Ensure Python 3.7+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Check if port 5000 is available

### Frontend can't connect to backend
- Ensure Flask server is running (you should see the startup message)
- Check that the API URL in `script.js` is `http://localhost:5000`
- Try accessing `http://localhost:5000/health` in your browser

### CORS errors
- The Flask server has CORS enabled via `flask-cors`
- If issues persist, try opening HTML from a local server instead of file://

## Running on a Different Port

To change the port, edit `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change 5000 to your port
```

And update `script.js`:

```javascript
const API_URL = 'http://localhost:5000';  // Change to match your port
```

## License

Free to use for educational and personal projects.

## Support

For issues or questions about the algorithm or implementation, please refer to:
- Karnaugh MAP logic documentation
- Boolean algebra fundamentals
- Digital logic design resources
