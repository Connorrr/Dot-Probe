import numpy as np

class CSVLogfileMaker:
    class __CSVLogfileMaker:
        def __init__(self, filename):
            self.filename = filename

        def set_filename(self, fname):
            self.filename = fname

        def set_column_names(self, column_names):
            self.data = column_names

        def add_row(self, row):
            #print(self.data)
            #print(row)
            self.data = np.append(self.data, row, axis=0)
            #print(self.data)

        def save_file(self):
            np.savetxt(self.filename, self.data, delimiter=',', fmt='%s')

    instance = None

    def __init__(self, filename='test1.csv'):
        if not self.instance:
            self.instance = self.__CSVLogfileMaker(filename)

    def set_filename(self, fname):
        self.instance.set_filename(fname)

    #  Must be called before add_row otherwise it will erase the data
    def set_column_names(self, column_names):
        self.instance.set_column_names(column_names)

    def add_row(self, row):
        self.instance.add_row(row)

    def save_file(self):
        self.instance.save_file()
