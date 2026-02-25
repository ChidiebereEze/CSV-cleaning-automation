import pandas as pd

def main():
    # Open CSV file
    input_folder = "input"
    filename = "List of Orders.csv"
    input_filepath = f"{input_folder}/{filename}"
    df = pd.read_csv(input_filepath)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Clean datatype/s
    df["order_date"] = pd.to_datetime(df ["order_date"], errors="coerce")

    # Dropping duplicates
    df = df.drop_duplicates()

    # Summary note
    print("Your dataframe has been cleaned")

    # Save CSV file
    output_folder = "output"
    filename = "list_of_orders_cleaned.csv"
    output_filepath = f"{output_folder}/{filename}"
    df.to_csv(output_filepath, index=False)
    print(f"Cleaned CSV file saved to {output_filepath}")

if __name__ == "__main__":
    main()