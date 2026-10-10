"""
AST Static analysis verification for Apex Rig.
Ensures zero external dependencies and 100% pure Python standard library.
"""

import ast
import os
import sys

ALLOWED_MODULES = {
    "abc", "argparse", "ast", "collections", "copy", "dataclasses",
    "deque", "enum", "heapq", "hashlib", "json", "math", "os", "platform",
    "random", "re", "shutil", "subprocess", "sys", "time", "typing",
    "unittest", "urllib", "uuid"
}


def scan_file(filepath: str) -> list:
    violations = []
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base = alias.name.split(".")[0]
                if base not in ALLOWED_MODULES and not base.startswith("apex_rig"):
                    violations.append((filepath, node.lineno, f"import {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base = node.module.split(".")[0]
                if base not in ALLOWED_MODULES and not base.startswith("apex_rig"):
                    violations.append((filepath, node.lineno, f"from {node.module} import ..."))
    return violations


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(root_dir, "apex_rig")
    all_violations = []

    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                v = scan_file(path)
                all_violations.extend(v)

    if all_violations:
        print(f"FAILED: Found {len(all_violations)} external dependency violations:")
        for path, line, stmt in all_violations:
            print(f"  {path}:{line} -> {stmt}")
        sys.exit(1)
    else:
        print("PASS: 100% pure Python standard library, zero external dependencies verified.")


if __name__ == "__main__":
    main()
