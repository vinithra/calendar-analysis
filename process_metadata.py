"""
Process collected categories to generate hints for future categorization.
"""

FILENAME = '/Users/vinithra/code/gcal/cloudera_cal_metadata.csv'

def process_file():
  """Read contents of file and process the contents
  """

  file_object = open(FILENAME, "r")
  read_categories(file_object)
  file_object.close()

def read_categories(file_object):
  """Read lines of the file and identify the categories
  """

  event_categories = {}
  for line in file_object:
    info = line.split("\t")
    event = info[0]
    category = info[4].replace("\n", "")
    categories = category.split(",")

    if event in event_categories:
      event_categories[event] = event_categories[event].append(categories)
    else:
      event_categories[event] = categories

  print(event_categories)

def main():
  process_file()


if __name__ == '__main__':
  main()
