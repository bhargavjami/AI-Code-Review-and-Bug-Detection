import ast
import re

def analyze_code(file_path):
    with open(file_path, "r") as f:
        code = f.read()

    try:
        tree = ast.parse(code)
    except Exception as e:
        return [f"❌ Error parsing file: {e}"]

    suggestions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if ast.get_docstring(node) is None:
                suggestions.append(f"👉 Function '{node.name}' is missing a docstring.")
            if len(node.body) > 15:
                suggestions.append(f"👉 Function '{node.name}' is too long ({len(node.body)} lines).")
            if len(node.args.args) > 4:
                suggestions.append(f"👉 Function '{node.name}' has too many arguments.")
            if not re.fullmatch(r'[a-z_][a-z0-9_]*', node.name):
                suggestions.append(f"👉 Function name '{node.name}' should be in snake_case.")

    assigned_vars = set()
    used_vars = set()
    bad_var_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned_vars.add(target.id)
                    if len(target.id) == 1 and target.id not in ['i', 'j', 'k']:
                        bad_var_names.add(target.id)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_vars.add(node.id)

    unused_vars = assigned_vars - used_vars
    for var in unused_vars:
        suggestions.append(f"👉 Variable '{var}' is assigned but never used.")
    for var in bad_var_names:
        suggestions.append(f"👉 Variable name '{var}' is too short. Use more descriptive names.")

    if not suggestions:
        suggestions.append("✅ No issues found. Code looks good!")

    return suggestions

# Run analysis on sample_code.py
results = analyze_code("sample_code.py")
print("Suggestions:")
for suggestion in results:
    print(suggestion)
