import pandas as pd

def read_file(file_path, file_type='csv', **kwargs):
    """
    Read different types of text files into a pandas DataFrame.
    
    Parameters:
    file_path (str): Path to the file
    file_type (str): Type of file ('csv', 'txt', 'excel', 'json', 'parquet')
    **kwargs: Additional arguments to pass to the reading function
    
    Returns:
    pandas.DataFrame: Data from the file
    """
    try:
        if file_type.lower() == 'csv':
            # Common CSV reading options
            default_options = {
                'encoding': 'utf-8',
                'sep': ',',
                'header': 0
            }
            default_options.update(kwargs)
            return pd.read_csv(file_path, **default_options)
            
        elif file_type.lower() == 'txt':
            # For fixed-width or custom-delimited text files
            default_options = {
                'encoding': 'utf-8',
                'sep': '\t',  # tab-delimited by default
                'header': 0
            }
            default_options.update(kwargs)
            return pd.read_table(file_path, **default_options)
            
        elif file_type.lower() == 'excel':
            # For Excel files (.xlsx, .xls)
            default_options = {
                'sheet_name': 0,  # First sheet by default
                'header': 0
            }
            default_options.update(kwargs)
            return pd.read_excel(file_path, **default_options)
            
        elif file_type.lower() == 'json':
            # For JSON files
            default_options = {
                'orient': 'records'
            }
            default_options.update(kwargs)
            return pd.read_json(file_path, **default_options)
            
        elif file_type.lower() == 'parquet':
            return pd.read_parquet(file_path, **kwargs)
            
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None

# Example usage:
if __name__ == "__main__":
    # Reading a CSV file
    df_csv = read_file('data.csv', file_type='csv')
    
    # Reading a CSV with specific options
    df_custom = read_file(
        'data.csv',
        file_type='csv',
        sep=';',  # semicolon-separated
        encoding='latin1',
        skiprows=2  # skip first two rows
    )
    
    # Reading an Excel file
    df_excel = read_file(
        'data.xlsx',
        file_type='excel',
        sheet_name='Sheet2'  # specify sheet name
    )
