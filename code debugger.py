import ast
import os
import time
import subprocess
from memory_profiler import memory_usage

class BugBountyDebugger:
    def __init__(self):
        self.issues = []

    def analyze_code(self, file_path):
        """
        Analyze the code for common issues such as time and space inefficiencies
        or logical errors. Reports syntax issues and potential inefficiencies.
        """
        try:
            with open(file_path, 'r') as file:
                code = file.read()

            tree = ast.parse(code)
            self._analyze_tree(tree)
        except SyntaxError as e:
            self.issues.append((e.lineno, f"SyntaxError: {e.msg}"))
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _analyze_tree(self, tree):
        """
        Traverse the AST to identify potential issues. This includes inefficiencies
        such as excessive loops, unused variables, or large functions.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                if isinstance(node.iter, (ast.Call, ast.List, ast.Set, ast.Tuple)):
                    self.issues.append((node.lineno, "Avoid iterating over potentially large collections in a for loop."))

            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 50:
                    self.issues.append((node.lineno, "Function is too large and may need refactoring."))
                if not any(isinstance(child, ast.Return) for child in ast.walk(node)):
                    self.issues.append((node.lineno, "Function lacks a return statement; consider adding one."))

            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.List) and len(node.value.elts) > 1000:
                    self.issues.append((node.lineno, "Avoid large in-memory lists; consider using generators."))

            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                if len(node.names) > 5:
                    self.issues.append((node.lineno, "Too many imports in a single statement; consider splitting them."))

            if isinstance(node, ast.While):
                self.issues.append((node.lineno, "While loops can cause infinite loops; ensure proper termination."))

            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if not self._is_variable_used(node, tree):
                    self.issues.append((node.lineno, f"Variable '{node.id}' is declared but never used."))

    def _is_variable_used(self, variable_node, tree):
        """
        Check if a variable is used anywhere in the AST tree after its declaration.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == variable_node.id and isinstance(node.ctx, ast.Load):
                return True
        return False

    def optimize_code(self, file_path):
        """
        Suggest optimizations based on the detected issues and provide actionable insights.
        """
        print(f"Analyzing {file_path} for optimization suggestions...\n")
        self.analyze_code(file_path)

        if self.issues:
            print(f"Detected {len(self.issues)} issues:\n")
            for lineno, issue in self.issues:
                print(f"Line {lineno}: {issue}")
        else:
            print("No issues detected. Your code looks efficient!")

    def benchmark_code(self, file_path):
        """
        Measure the execution time and memory usage of the script, providing both
        a detailed report and actionable insights.
        """
        print(f"Benchmarking {file_path}...\n")

        try:
            start_time = time.time()
            mem_usage = memory_usage((subprocess.run, ("python", [file_path]), {}), interval=0.1)
            end_time = time.time()

            execution_time = end_time - start_time
            max_memory = max(mem_usage)

            print(f"Execution Time: {execution_time:.2f} seconds")
            print(f"Peak Memory Usage: {max_memory:.2f} MiB")
        except Exception as e:
            print(f"Error during benchmarking: {e}")

    def analyze_project(self, directory_path):
        """
        Analyze all Python files in a given directory. This includes subdirectories
        and provides a comprehensive report of the entire project.
        """
        print(f"Analyzing project at {directory_path}...\n")
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    print(f"Analyzing {file_path}...")
                    self.optimize_code(file_path)

    def generate_report(self, output_path="debug_report.txt"):
        """
        Generate a detailed report of the identified issues and optimizations.
        """
        print(f"Generating report at {output_path}...\n")
        try:
            with open(output_path, "w") as report_file:
                if self.issues:
                    report_file.write("Detected Issues:\n")
                    for lineno, issue in self.issues:
                        report_file.write(f"Line {lineno}: {issue}\n")
                else:
                    report_file.write("No issues detected. The code appears efficient!\n")
            print("Report generation completed successfully.")
        except Exception as e:
            print(f"Error generating report: {e}")

if __name__ == "__main__":
    debugger = BugBountyDebugger()

    user_input = input("Enter the path of the Python file or directory to debug: ").strip()
    if os.path.exists(user_input):
        if os.path.isfile(user_input):
            debugger.optimize_code(user_input)
            debugger.benchmark_code(user_input)
            debugger.generate_report()
        elif os.path.isdir(user_input):
            debugger.analyze_project(user_input)
            debugger.generate_report()
        else:
            print("Invalid path provided.")
    else:
        print("File or directory does not exist. Please check the path.")
