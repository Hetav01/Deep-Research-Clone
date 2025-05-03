import os
import getpass
import pdfkit
import markdown2

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

def save_report_as_markdown(report_markdown: str, output_filename: str):
    """
    Saves a Markdown report to a file.

    Args:
        report_markdown (str): The report content in Markdown format.
        output_filename (str): The name of the output Markdown file (including path).

    Returns:
        str: The path to the saved Markdown file.
    """
    try:
        # Define the output directory
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write the Markdown content to the file
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(report_markdown)

        return output_filename
    except Exception as e:
        raise RuntimeError(f"Failed to save report as Markdown: {e}")

_set_env("TAVILY_API_KEY")