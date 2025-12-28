"""
Manual citation source plugin.

This file is part of the Lab Website Template citation pipeline. It passes
through manually defined citation entries (e.g., items not available on PubMed).
"""

def main(entry):
    """
    receives single list entry from sources data file
    returns list of sources to cite
    """
    return [entry]
