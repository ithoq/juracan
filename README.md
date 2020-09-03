# juracan

usage: juracan_0.7.py [-h] [-s dbpath tablename]
                      [-m host dbname tblname user password] [-c] [-r]
                      [keyword]

Gets ASN and ISP addresses related to the target keyword from the Hurricane
Electric Internet Services website. Please do not abuse this service!

positional arguments:
  keyword               target keyword

optional arguments:
  -h, --help            show this help message and exit
  -s dbpath tablename, --sqlite dbpath tablename
                        store results in a SQLite database; creates a new
                        database and table if they don't already exist
  -m host dbname tblname user password, --mysql host dbname tblname user password
                        store results in a MySQL database; creates a new
                        database and table if they don't exist
  -c, --csv             output table data as a CSV list
  -r, --result          output the result column data only; if --csv is on,
                        result column data is output as a CSV list
