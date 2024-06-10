import pandas as pd


def combine():
    # List of CSV files to be combined
    files = [
        'finished_reddit_data_AskDocs.csv',
        'finished_reddit_data_askCardiology.csv',
        'finished_reddit_data_Heartfailure.csv',
        'finished_reddit_data_pacemakericd.csv']

    # Initialize an empty list to store the dataframes
    dataframes = []

    for file in files:
        # Read the current CSV file into a dataframe
        df = pd.read_csv(file)
        # Append the dataframe to the list
        dataframes.append(df)

    # Concatenate all the dataframes in the list
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Specify the output file name
    output_file = 'combined_reddit_data.csv'

    # Save the combined dataframe to a new CSV file
    combined_df.to_csv(output_file, index=False)

    print(f"All files have been successfully combined into {output_file}")

    #assign random names to participants
    csv_file = 'combined_reddit_data.csv'

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Create a dictionary to hold unique names and assign them a participant number
    participant_map = {}
    current_participant_id = 1

    # Loop through each name in the first column
    for name in df.iloc[:, 0]:
        if name not in participant_map:
            # Assign a new participant number to the name
            participant_map[name] = f'Participant {current_participant_id}'
            current_participant_id += 1

    # Map the names in the first column to their corresponding participant numbers
    df.iloc[:, 0] = df.iloc[:, 0].map(participant_map)

    # Save the deidentified data back to a new CSV file
    deidentified_file = 'deidentified_participants.csv'
    df.to_csv(deidentified_file, index=False)

    print(f"Data has been successfully deidentified and saved to {deidentified_file}")