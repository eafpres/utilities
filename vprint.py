#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 09:32:24 2025

@author: eafpres
"""
#%% required libraries
#
import pandas as pd
import os
#
#%% terminal print with long column names
#
def vprint(df: pd.DataFrame = None,
           max_width: int = None):
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
  if df is None:
    return
#
# make a copy so index changes don't affect original
#
  df = df.copy()
#
# some constants (can be changed, ultimately
#                 could be parameterized)
#
  whitespace = 1
  min_colwidth = 3
#
# if there is "extra space" (see code) then
# the longer columns are grouped by max data length
# into n groups, sorted by max data length,
# and priority to increase width is given to
# the longer groups first
#
  num_groups_to_adjust = 3
#
# determine the available width (either from terminal or user input)
#
  if max_width is None:
    try:
      max_width = os.get_terminal_size().columns
    except OSError:
      max_width = 80
#
# rename index levels to ensure unique names
# and to highlight index columns
#
  padding = '||v'
  iname = '-index- '
  if isinstance(df.index, pd.MultiIndex):
    index_names = [
      f'{iname}{name}{padding}' if name is not None
      else f'{iname}{i}{padding}'
      for i, name in enumerate(df.index.names)
    ]
    df.index.names = index_names
  elif df.index.name is None:
    df.index.name = f'{iname}0{padding}'
    index_names = [df.index.name]
  else:
    df.index.name = f'{iname}{df.index.name}{padding}'
    index_names = [df.index.name]
#
# make the index into column(s)
#
  df = df.reset_index(drop = False)
#
# sparsify as done in Pandas
#
  df[index_names[0]] = ([df[index_names[0]][0]] +
                        [df[index_names[0]][i]
                         if df[index_names[0]][i] != df[index_names[0]][i - 1]
                         else ' '
                         for i in range(1, df.shape[0])])
#
# initially adjust min_colwidth to max average available
#
  ncols = df.shape[1]
  min_colwidth = max(min_colwidth,
                     (max_width - ncols * whitespace - whitespace) // ncols)
  if min_colwidth < 3:
    print(
      ' '.join(f'''cannot vprint;
                   the minimum column width would be {min_colwidth}:
                   suggest using print()'''.split())
                   )
    return
#
# adjust min_colwidth if there is room
#
  def measure(col_val):
    width = len(str(col_val))
    return width
  data_widths = [max(df[col].apply(measure))
                 for col in df.columns]
  min_needed_space = sum([width + whitespace if width <= min_colwidth
                          else min_colwidth + whitespace
                          for width in data_widths])
  if min_needed_space > max_width:
    print(
      ' '.join(f'''cannot vprint;
                   needed space ({min_needed_space}) >
                   max width ({max_width}):
                   suggest using print()'''.split())
                   )
    return
#
# if the number of rows exceeds max_rows, limit rows like pandas would
#
# get the max rows from pandas settings
#
  max_rows = pd.get_option('display.max_rows')
#
  if (max_rows is not None) and (len(df) > max_rows):
    head = df.head(max_rows // 2)
    tail = df.tail(max_rows // 2)
    placeholder = \
      pd.DataFrame([['...'] * len(df.columns)], columns = df.columns)
    df = \
      pd.concat([head, placeholder, tail], ignore_index = True)
  else:
    ...
#
# try to add width to wider columns
#
  col_widths = [min_colwidth] * ncols
  extra_space = max_width - min_needed_space
  col_widths = [data_widths[i]
                if data_widths[i] <= min_colwidth
                else col_widths[i]
                for i in range(len(col_widths))]
  cols_to_adjust = [col_no
                    for col_no, col_width in enumerate(data_widths)
                    if col_width > min_colwidth]
#
# indices of cols to adjust in order of increasing max width of data
#
  def split(lst, chunks):
    k, m = divmod(len(lst), chunks)
    return [lst[i * k + min(i, m):
                (i + 1) * k + min(i + 1, m)]
          for i in range(chunks)]
  groups_to_adjust = \
    split([sorted([(data_widths[col_to_adjust],
                    col_to_adjust)
                   for col_to_adjust in cols_to_adjust])[i][1]
           for i in range(len(cols_to_adjust))],
          num_groups_to_adjust)
  groups_to_adjust = [group
                      for group in groups_to_adjust
                      if group != []]
  while ((extra_space > 0) &
         (sum([col_widths[item]
               for group in groups_to_adjust
               for item in group]) <
          sum([data_widths[item]
               for group in groups_to_adjust
               for item in group]))):
    for group in groups_to_adjust[::-1]:
      for col in group:
        if extra_space > 0:
          if col_widths[col] < data_widths[col]:
            col_widths[col] += 1
            extra_space -= 1
#
# apply truncation to the DataFrame
#
# truncate cell values according to col_widths
#
  def truncate(val, width):
    val_str = str(val)
    if len(val_str) > width:
      return val_str[:width]
    else:
      return val_str
  df = \
    pd.DataFrame(pd.concat([df.iloc[:, col].
                            apply(lambda x: truncate(x, col_widths[col]))
                            for col in range(df.shape[1])],
                           axis = 1),
                 columns = df.columns)
#
# determine height needed for the tallest column name
#
  max_height = max(len(col) for col in df.columns)
#
# create vertically stacked header
#
  rotated_header_lines = []
  for i in range(max_height):
    line = []
    for colnum, (col, width) in enumerate(zip(df.columns, col_widths)):
      if i < (max_height - len(col)):
        line.append(' ' * (width + whitespace))
      else:
        char = col[i - (max_height - len(col))]
        if colnum < ncols:
          line.append(char.ljust(width + whitespace))
        else:
          line.append(char.ljust(width))
    rotated_header_lines.append(''.join(line))
#
# print the header
#
  for line in rotated_header_lines:
    print(line.rstrip())
#
# seperator
#
  print('-' * (sum(col_widths) +
               ncols * whitespace -
               whitespace))
#
# print each row
#
  for _, row in df.iterrows():
    row_str = ''.join(str(val).ljust(width + whitespace)
                      for val, width in zip(row, col_widths))
    print(row_str.rstrip())
#
  return
#
#%% run from cli
#
if __name__ == '__main__':
  import pandas as pd
  max_width = 159
  max_rows = 17
  pd.set_option('display.width', max_width)
  pd.set_option('display.max_rows', max_rows)
  print(f'running example with max width {max_width} and max rows {max_rows}')
  data = pd.read_csv('./data/housing_prices_train.csv',
                     usecols = ['MSSubClass',
                                'MSZoning',
                                'LotFrontage',
                                'LotArea',
                                'Street',
                                'Alley',
                                'LotShape',
                                'Utilities',
                                'Neighborhood',
                                'Condition1',
                                'BldgType',
                                'HouseStyle',
                                'OverallQual',
                                'OverallCond',
                                'YearBuilt',
                                'RoofStyle',
                                'RoofMatl',
                                'Exterior1st',
                                'Exterior2nd',
                                'MasVnrType',
                                'MasVnrArea',
                                'TotRmsAbvGrd',
                                'Fireplaces',
                                'GarageType',
                                'GarageArea',
                                'PavedDrive',
                                'WoodDeckSF',
                                'OpenPorchSF',
                                'EnclosedPorch',
                                'PoolArea',
                                'PoolQC',
                                'Fence',
                                'MoSold',
                                'YrSold',
                                'SaleType',
                                'SaleCondition'])
#
# create mixed types
#
  data.iloc[3:5, 12] = 9999
#
# add duplicate row for showing sparse multi-index
#
  data = pd.concat([data.iloc[:5, :],
                    data.iloc[4:, :]],
                   axis = 0)
  vprint(data, max_width = max_width)
  print()
#
  vprint(data[['MSSubClass',
               'LotShape',
               'OverallQual',
               'OverallCond',
               'TotRmsAbvGrd',
               'MasVnrType',
               'GarageType',
               'SaleCondition']])