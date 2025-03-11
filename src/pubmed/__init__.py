import argparse

def main():
    
    parser = argparse.ArgumentParser(description="Custom CLI app")
    # parser.add_argument("-h", "--help", action="store_true", help="Show custom help message.")
    
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug information during execution.")
    parser.add_argument("-f", "--file", type=str, help="Specify the filename to save the results. If not provided, print the output to the console.")
    

    args = parser.parse_args()
    
    # if args.help:
    #     print("custom")
    if args.debug:
        print("Debug mode is ON.")
    

    if args.file:
        with open(args.file, "w") as file:
            file.write("Results saved to this file.")
        print(f"Results saved to {args.file}.")
    else:
        print("Results printed to the console.")

if __name__ == "__main__":
    main()
