import ast
import re

def analyze_code(file_path):
    try:
        with open(file_path, "r") as f:
            code = f.read()
    except FileNotFoundError:
        return [f"❌ File '{file_path}' not found."]
    
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

# ------------------ CLI Menu ------------------

print("🔍==== AI Code Reviewer ====")
filename = input("Enter the Python file to analyze (e.g., sample_code.py): ").strip()
results = analyze_code(filename)

print("\nSuggestions:")
for suggestion in results:
    print(suggestion)

save = input("\nDo you want to save the report to review_report.txt? (y/n): ").lower()
if save == 'y':
    with open("review_report.txt", "w", encoding="utf-8") as f:
        f.write("Code Review Report:\n")
        for suggestion in results:
            f.write(suggestion + "\n")
    print("✅ Suggestions saved to review_report.txt")
