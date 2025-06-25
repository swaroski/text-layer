""""""

import click
import os
import sys
import logging

from app import create_app

from dotenv import load_dotenv

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Create flask app
app = create_app(os.getenv('FLASK_CONFIG') or 'DEV')

@app.cli.command()
@click.option(
    "--coverage/--no-coverage",
    default=False,
    help="Run tests under code coverage.",
)
@click.argument("test_names", nargs=-1)
def test(coverage, test_names):
    """Run the unit tests."""
    from app.cli import run_tests

    test_results = run_tests(coverage, test_names)

    if test_results.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    # Allows running `python cli.py test` directly if needed
    app.cli()