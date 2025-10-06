import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(project_root, 'templates')
static_dir = os.path.join(project_root, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app)  # Enable CORS for frontend communication

def decimal_to_binary(num, num_vars):
    """Convert decimal to binary with padding"""
    return format(num, f'0{num_vars}b')

def count_ones(binary):
    """Count ones in binary string"""
    return binary.count('1')

def differ_by_one_bit(bin1, bin2):
    """Check if two binary strings differ by exactly one bit"""
    diff_count = 0
    diff_pos = -1
    
    for i in range(len(bin1)):
        if bin1[i] != bin2[i]:
            diff_count += 1
            diff_pos = i
    
    return diff_count == 1, diff_pos

def group_by_ones(terms):
    """Group terms by number of ones"""
    groups = {}
    for term in terms:
        ones = count_ones(term['binary'])
        if ones not in groups:
            groups[ones] = []
        groups[ones].append(term)
    return groups

def find_prime_implicants(minterms, dont_cares, num_vars):
    """Find prime implicants using Karnaugh MAP logic"""
    # Convert all terms to binary
    all_terms = []
    minterm_set = set(minterms)
    
    for m in minterms:
        all_terms.append({
            'binary': decimal_to_binary(m, num_vars),
            'decimals': {m},
            'used': False,
            'dont_care': False
        })
    
    for d in dont_cares:
        all_terms.append({
            'binary': decimal_to_binary(d, num_vars),
            'decimals': {d},
            'used': False,
            'dont_care': True
        })
    
    current_terms = all_terms
    prime_implicants = []
    prime_implicant_coverage = []
    
    # Iteratively combine terms
    while len(current_terms) > 0:
        groups = group_by_ones(current_terms)
        new_terms = []
        combined = {}
        
        # Try to combine terms from adjacent groups
        sorted_keys = sorted(groups.keys())
        
        for i in range(len(sorted_keys) - 1):
            group1 = groups[sorted_keys[i]]
            group2 = groups[sorted_keys[i + 1]]
            
            for term1 in group1:
                for term2 in group2:
                    can_combine, diff_pos = differ_by_one_bit(term1['binary'], term2['binary'])
                    
                    if can_combine:
                        term1['used'] = True
                        term2['used'] = True
                        
                        # Create new term with '-' at difference position
                        new_binary = term1['binary'][:diff_pos] + '-' + term1['binary'][diff_pos + 1:]
                        combined_decimals = term1['decimals'] | term2['decimals']
                        
                        if new_binary not in combined:
                            combined[new_binary] = {
                                'binary': new_binary,
                                'decimals': combined_decimals,
                                'used': False,
                                'dont_care': term1['dont_care'] and term2['dont_care']
                            }
                        else:
                            combined[new_binary]['decimals'] |= combined_decimals
        
        new_terms = list(combined.values())
        
        # Add unused terms as prime implicants
        for term in current_terms:
            if not term['used']:
                # Check if this prime implicant covers any actual minterms
                covered_minterms = term['decimals'] & minterm_set
                if covered_minterms:
                    prime_implicants.append(term['binary'])
                    prime_implicant_coverage.append(covered_minterms)
        
        current_terms = new_terms
    
    return prime_implicants, prime_implicant_coverage


def find_essential_prime_implicants(prime_implicants, coverage, minterms):
    """Find essential prime implicants using coverage table"""
    if not prime_implicants:
        return []
    
    minterm_set = set(minterms)
    uncovered = minterm_set.copy()
    essential = []
    essential_indices = set()
    
    # Find essential prime implicants (those that uniquely cover a minterm)
    for minterm in minterm_set:
        covering_pis = [i for i, cov in enumerate(coverage) if minterm in cov]
        if len(covering_pis) == 1:
            pi_index = covering_pis[0]
            if pi_index not in essential_indices:
                essential_indices.add(pi_index)
                essential.append(prime_implicants[pi_index])
                uncovered -= coverage[pi_index]
    
    # If all minterms are covered by essential PIs, return them
    if not uncovered:
        return essential
    
    # Otherwise, use greedy approach to cover remaining minterms
    remaining_pis = [(i, pi, cov) for i, (pi, cov) in enumerate(zip(prime_implicants, coverage)) 
                     if i not in essential_indices]
    
    while uncovered and remaining_pis:
        # Find PI that covers the most uncovered minterms
        best_pi = max(remaining_pis, key=lambda x: len(x[2] & uncovered))
        essential.append(best_pi[1])
        uncovered -= best_pi[2]
        remaining_pis.remove(best_pi)
    
    return essential

def binary_to_expression(binary, variables):
    """Convert binary implicant to Boolean expression with correct formatting"""
    terms = []
    
    for i in range(len(binary)):
        if binary[i] == '1':
            terms.append(variables[i])
        elif binary[i] == '0':
            terms.append(variables[i] + "'")
        # Skip '-' (don't care positions)
    
    # Sort alphabetically: first by base letter, then non-complemented before complemented
    terms.sort(key=lambda x: (x.replace("'", ""), "'" in x))
    
    return ''.join(terms)

def simplify_boolean(minterms, num_vars, mode='SOP', dont_cares=None):
    """
    Simplify Boolean expression using Karnaugh MAP logic
    
    Args:
        minterms: List of minterms/maxterms
        num_vars: Number of variables (2-4)
        mode: 'SOP' or 'POS'
        dont_cares: List of don't care terms
    
    Returns:
        Simplified Boolean expression as string with correct formatting
    """
    if dont_cares is None:
        dont_cares = []
    
    variables = ['A', 'B', 'C', 'D'][:num_vars]
    
    # Handle empty minterms
    if len(minterms) == 0:
        return '0' if mode == 'SOP' else '1'
    
    # For POS, convert to minterms (complement)
    working_minterms = minterms
    if mode == 'POS':
        max_term = 2 ** num_vars
        all_terms = list(range(max_term))
        working_minterms = [t for t in all_terms if t not in minterms and t not in dont_cares]
    
    # Find prime implicants with coverage information
    prime_implicants, coverage = find_prime_implicants(working_minterms, dont_cares, num_vars)
    
    # Find minimal set of prime implicants
    essential_implicants = find_essential_prime_implicants(prime_implicants, coverage, working_minterms)
    
    # Convert to expressions
    expressions = []
    for pi in essential_implicants:
        expr = binary_to_expression(pi, variables)
        if expr:
            expressions.append(expr)
    
    # Sort expressions
    expressions.sort()
    
    # Format based on mode
    if mode == 'SOP':
        simplified = ' + '.join(expressions) if expressions else '1'
    else:
        # For POS, wrap each term in parentheses and convert to OR
        pos_terms = []
        for expr in expressions:
            converted_terms = []
            i = 0
            while i < len(expr):
                char = expr[i]
                if i + 1 < len(expr) and expr[i + 1] == "'":
                    # Complemented variable - remove complement
                    converted_terms.append(char)
                    i += 2
                else:
                    # Non-complemented variable - add complement
                    converted_terms.append(char + "'")
                    i += 1
            pos_terms.append('(' + ' + '.join(converted_terms) + ')')
        
        simplified = ' · '.join(pos_terms) if pos_terms else '0'
    
    return simplified

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simplify', methods=['POST'])
def simplify():
    """API endpoint for Boolean simplification"""
    try:
        data = request.get_json()
        
        # Extract parameters
        minterms = data.get('minterms', [])
        num_vars = data.get('num_vars', 3)
        mode = data.get('mode', 'SOP')
        dont_cares = data.get('dont_cares', [])
        
        # Validation
        if not isinstance(minterms, list) or len(minterms) == 0:
            return jsonify({'error': 'Minterms must be a non-empty list'}), 400
        
        if num_vars < 2 or num_vars > 4:
            return jsonify({'error': 'Number of variables must be between 2 and 4'}), 400
        
        if mode not in ['SOP', 'POS']:
            return jsonify({'error': 'Mode must be either SOP or POS'}), 400
        
        # Validate term ranges
        max_term = 2 ** num_vars - 1
        all_terms = minterms + dont_cares
        
        for term in all_terms:
            if not isinstance(term, int) or term < 0 or term > max_term:
                return jsonify({
                    'error': f'Term {term} is out of range. Valid range: 0-{max_term}'
                }), 400
        
        # Check for duplicates
        if len(set(all_terms)) != len(all_terms):
            return jsonify({'error': 'Duplicate terms found'}), 400
        
        # Perform simplification
        simplified = simplify_boolean(minterms, num_vars, mode, dont_cares)
        
        # Prepare response
        var_names = ['A', 'B', 'C', 'D'][:num_vars]
        
        return jsonify({
            'simplified': simplified,
            'variables': var_names,
            'original_terms': sorted(minterms),
            'dont_cares': sorted(dont_cares),
            'mode': mode
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Boolean Simplifier API is running'})

if __name__ == '__main__':
    print("🚀 Starting Boolean Simplifier API...")
    print("📡 Server running at http://localhost:5000")
    print("🔗 Open index.html in your browser to use the app")
    app.run(debug=True, host='0.0.0.0', port=5000)
