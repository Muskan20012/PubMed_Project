from src.pubmed.module import query_pubmed


def main():
    import argparse
    import json
    example="""
    EXAMPLE:

        get-papers-list -q "DNA" -f results.csv
        Search for "DNA" papers and save the results to results.csv

        get-papers-list -q "DNA" -d
        Search for "DNA" papers with debug mode enabled.
"""
    parser = argparse.ArgumentParser(
        prog='PUBMED CLI',
        description="A command-line tool for querying PubMed articles and fetching detailed information.",
        epilog=example,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    parser.add_argument("-q", "--query", type=str, required=True, help="Specify the search query for PubMed.")
    parser.add_argument("-f", "--file", type=str, help="Save the results to a CSV file instead of printing them.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode for additional output.")

    args = parser.parse_args()

    try:
        results = query_pubmed(args.query, debug=args.debug)
        if args.file:
            with open(args.file, "w") as file:
                json.dump(results, file, indent=4)
            print(f"Results saved to {args.file}")
        else:
            print("Results:")
            print(json.dumps(results, indent=4))
    except RuntimeError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
