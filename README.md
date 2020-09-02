# juracan

usage: juracan_0.3.py [-h] [--sqlite dbpath tablename]
                      [--mysql host dbname tblname user password]
                      [keyword]

Gets ASN and ISP addresses related to the target keyword from the Hurricane
Electric Internet Services website. Please do not abuse this service!

positional arguments:
  keyword               target keyword

optional arguments:
  -h, --help	>	show this help message and exit
  --sqlite dbpath tablename	>	store results in a SQLite database
  --mysql host dbname tblname user password	>	store results in a MySQL database
