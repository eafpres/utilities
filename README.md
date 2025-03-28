# utilities

vprint.py:
  """Print a pandas DataFrame with column headers rotated vertically.

  Respects pandas display option `max_rows`.
  Rotates column headers so that they are printed vertically (stacked),
  which can be helpful when there are many columns and/or long column names.
  Will attempt to provide extra width to columns with long data.
  The index is printed with the index names flagged as -index- {name}.
  MultiIndex is supported.

  If `max_width` is provided, it limits the total printed width in characters,
  otherwise, the terminal width is used as a default, or 80 if it cannot
  be determined.

  Args:
      df (pd.DataFrame): The DataFrame to print.
                         If no DataFrame is provided, will return silently.
      max_width (int, optional): Maximum width (in characters)
                                 of the printed table.
                                 Defaults to terminal width.

  """
usage:
data = pd.read_csv(./data/housing_data_train.py)
vprint(data, max_width = 159)
  vprint(data[['MSSubClass',
               'LotShape',
               'OverallQual',
               'OverallCond',
               'TotRmsAbvGrd',
               'MasVnrType',
               'GarageType',
               'SaleCondition']], 
          max_width = 159)

Note: if called with max_width exceeding terminal width text will wrap creating a **terrible** view
Note: if the given columns cannot fit into the max_width the function will report so and return
