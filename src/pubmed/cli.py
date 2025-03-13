import argparse
import asyncio
import csv
from typing import Any, Dict, List
from itertools import cycle
from src.pubmed.api import fetch_filtered_articles


def main() -> None:
    example: str = """
    EXAMPLE:

        get-papers-list -q "DNA" -f results.csv
        Search for "DNA" papers and save the results to results.csv

        get-papers-list -q "DNA" -d
        Search for "DNA" papers with debug mode enabled.

        get-papers-list -q "DNA" -n 10
        Search for a total of 10 "DNA" papers.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="PUBMED CLI",
        description="A command-line tool for querying PubMed articles and fetching detailed information.",
        epilog=example,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-q", "--query", type=str, required=True, help="Specify the search query for PubMed.")
    parser.add_argument("-f", "--file", type=str, help="Save the results to a CSV file instead of printing them.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode for additional output.")
    parser.add_argument("-n", "--number", type=int,required=True, help="Tell the number of articles required.")

    args: argparse.Namespace = parser.parse_args()

    async def show_loading() -> None:
        """
        Display a loading animation in the console.
        """
        for symbol in cycle(["|", "/", "-", "\\"]):
            print(f"\rLoading {symbol}", end="", flush=True)
            await asyncio.sleep(0.1)

    async def run() -> None:
        """
        Asynchronous function to fetch articles and save or print results.
        """
        loading_task: asyncio.Task | None = None

        try:
            if not args.file:
                loading_task = asyncio.create_task(show_loading())

            articles: List[Dict[str, Any]] = await fetch_filtered_articles(
                query=args.query, desired_count=args.number, debug=args.debug
            )

            if loading_task:
                loading_task.cancel()
                await asyncio.sleep(0.1)  
                print("\r" + " " * 20 + "\r", end="", flush=True)  

            if args.file:
                with open(args.file, "w", newline="", encoding="utf-8") as csvfile:
                    fieldnames: List[str] = [
                        "PubMed ID", "Title", "Authors", "Date", "Company", "Corresponding Author Email"
                    ]
                    writer: csv.DictWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for article in articles:
                        writer.writerow({
                            "PubMed ID": article.get("PubmedID", ""),
                            "Title": article.get("Title", ""),
                            "Authors": article.get("Authors", ""),
                            "Date": article.get("Publication Date", ""),
                            "Company": article.get("Company", ""),
                            "Corresponding Author Email": article.get("Corresponding Author Email", ""),
                        })
                print(f"Results saved to {args.file}")
            else:
                for article in articles:
                    print("\n--- Article Details ---")
                    for key, value in article.items():
                        print(f"■ {key}: {value}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            if loading_task:
                loading_task.cancel()
            print(f"Error: {e}")

    asyncio.run(run())


if __name__ == "__main__":
    main()
