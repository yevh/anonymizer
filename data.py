import random
import pandas as pd

data_with_underscore_columns = {
    'ID': [1, 2, 3, 4, 5],
    'First_Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Last_Name': ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown'],
    'Address': ['123 Main St', '456 Oak Rd', '789 Pine Ave', '101 Maple Dr', '202 Elm St'],
    'City': ['Springfield', 'Shelbyville', 'Ogdenville', 'North Haverbrook', 'Capital City'],
    'State': ['IL', 'TN', 'NY', 'FL', 'TX'],
    'Zip': ['62704', '37160', '13669', '33411', '73301'],
    'Phone': ['217-555-1234', '931-555-5678', '315-555-7890', '561-555-2468', '512-555-1357'],
    'Email': ['alice@email.com', 'bob@email.com', 'charlie@email.com', 'david@email.com', 'eve@email.com'],
    'SSN': ['123-45-6789', '234-56-7890', '345-67-8901', '456-78-9012', '567-89-0123'],
    'Credit_Card': ['1234-5678-9012-3456', '2345-6789-0123-4567', '3456-7890-1234-5678', '4567-8901-2345-6789', '5678-9012-3456-7890'],
    'Order_Amount': [150.50, 200.75, 350.20, 275.65, 300.25],
    'Order_Date': ['2023-08-01', '2023-08-02', '2023-08-03', '2023-08-04', '2023-08-05']
}

datafile_with_underscore_columns_df = pd.DataFrame(data_with_underscore_columns)

datafile_with_underscore_columns_path = "data.csv"
datafile_with_underscore_columns_df.to_csv(datafile_with_underscore_columns_path, index=False)

datafile_with_underscore_columns_df, datafile_with_underscore_columns_path

