asciiart
========

A python library and command-line pipe tool to handle [ASCII-Art](http://en.wikipedia.org/wiki/ASCII_art) to Text conversions.

Features
--------

* ***Encoding***: convert from string to ascii-art.
* ***Decoding***: convert from ascii-art to string.
* ***Customizable charsets***: the user may specify a `.charset` file via the `-c` switch to select which characters will be supported. `decimal.charset` is used by default (digits 0-9), `hex.charset` is also provided (digits 0-9 and a-f, for hexadecimal base).
* ***Illegal character indicators***: Whenever an invalid ascii-art character (block) is encountered, it is replaced by a special indicator (`?` by default).
* ***Illegal character line indicators***: When a line with at least one illegal block is decoded, this indicator will be appended to it (` ILLEGAL` by default).
* ***Block error tolerance***: Whenever an invalid ascii-art character (block) is encountered, the program can attempt to fix it buy matching it to a similar block character 'drawing'. The tolerance of the distance function is configurable by a parameter.
* ***Variable line/block-line width***: The pipe can handle lines of different widths (both in plaintext and ascii-art forms). Incase a single ascii-art block-line (typically 4 lines high) varies in its line widths, an error is thrown. The last line in a ascii-art block line (typically the 4th line in the plaintext) may be empty or at the exact correct width.

Requirements
------------

The program requires python 2.7.x, with no special libraries.

Usage
-----

The program (asciiart.py) is a command-line pipe (receives input via stdin, outputs to stdout). It may do both encoding (string to ASCII art) and decoding (ASCII art to string) operations.

Detailed usage instructions (from `python asciiart.py -h`):

    usage: asciiart.py [-h] [--charset CS] [--tolerance T] [--no-illegal]
                       [--invalid_char C]
                       {encode,decode}

    Text <--> ASCII Art conversion pipe (stdin --> stdout)

    positional arguments:
      {encode,decode}   encode: ascii-art --> text, decode: text --> ascii-art

    optional arguments:
      -h, --help        show this help message and exit
      --charset CS      selects file CS as the ascii-art charset
      --tolerance T     conversion will tolerate errors of up to distance T
      --no-illegal      will not print the ILLEGAL suffix in-case of errors
      --invalid_char C  will use C to indicate an unrecognized ascii-art block

Critical errors (e.g. bad file formats, invalid spacing, etc.), trigger an exception, promptly terminating the program.

Examples
--------

### Encoding (decimal to ascii-art) ###
Encoding the decimal data in `ex1_decimal.txt` will yield the results found in `ex1_art.txt`:

    python asciiart.py encode < ex1_decimal.txt > ex1_art.txt

Output (in `ex1_art.txt`):

        _  _  _     _  _ 
      ||_  _||_ |_| _||_ 
      ||_||_  _|  | _| _|
                         
           _    
      |  | _|  |
      |  ||_   |
                


### Decoding (ascii-art to decimal) ###

Decoding the ascii-art data in `ex1_art.txt` will yiedl the results found in `ex1_decimal.txt`:

    python asciiart.py decode < ex1_art.txt > ex1_decimal.txt

Output (in `ex1_decimal.txt`):

    1625435
    1121


### Encoding from directly from stdin ###

Input may be written directly to the command line, and terminated by an EOF character (`Ctrl+Z`):

    python asciiart.py encode
    72672221
    45391023
    ^Z

Output (same as `ex2_art.txt`):
        
     _  _  _  _  _  _  _
      | _||_   | _| _| _|  |
      ||_ |_|  ||_ |_ |_   |
    
        _  _  _     _  _  _
    |_||_  _||_|  || | _| _|
      | _| _| _|  ||_||_  _|
    
    
### Decoding erroneous input ###

Incase of decoding errors, a '?' character replaces all unrecognized characters, and an ' INVALID' string is appended to the end of the decoded line. In `ex2_art_error1.txt`, the `2` digits in the first line have their middle line removed:

    python asciiart.py decode < ex2_art_error1.txt > ex2_decimal_error1.txt


Output:
    
    7267???1 ILLEGAL
    45391023
    

### Controlling error indications ###

We can customize the error indication character (default '?') to some other character (in this example we will use '_') using the `--invalid_char` option, and remote the ' ILLEGAL' suffixes using the `--no-illegal` switch:
    
    python asciiart.py decode --invalid_char _ --no-illegal < ex2_art_error1.txt
    
Output:
    
    7267___1
    45391023
    
### Automatically fixing errors ###

We can instruct the program to automatically attempt to fix erroneous block characters (ascii-art), by replacing these with visually-similar blocks. For example, in the erronous input inside `ex2_art_error1.txt`, the program will recognize the bad '2' characters in the first line are only one character apart from the good representation of '2'. By increasing the error tolerance from the default 0 to 1 (`--tolerance 1`), we will automatically fix these errors:

    python asciiart.py decode --tolerance 1 < ex2_art_error1.txt > ex2_decimal_error1_recovered.txt

Output (in `ex2_decimal_error1_recovered.txt`):
    
    72672221
    45391023
    

### Using different charsets (hexadecimal) ###

We can select charsets different from the default decimal (`decimal.charset`), by using the `--charset` switch. In this example, we will use a hexadecimal charset (0-9 and a-f):
    
    python asciiart.py encode --charset hex.charset < ex3_hex.txt > ex3_art.txt
    
Input (in `ex3_hex.txt`):

    deadbeef
    2377992020
    6d92d
    fffffff
 
Output (in `ex3_art.txt`):

        _  _        _  _  _
     _||_ |_| _||_ |_ |_ |_
    |_||_ | ||_||_||_ |_ |
    
     _  _  _  _  _  _  _  _  _  _
     _| _|  |  ||_||_| _|| | _|| |
    |_  _|  |  | _| _||_ |_||_ |_|
    
     _     _  _
    |_  _||_| _| _|
    |_||_| _||_ |_|
    
     _  _  _  _  _  _  _
    |_ |_ |_ |_ |_ |_ |_
    |  |  |  |  |  |  |
    

All other flags previously exemplified work exactly the same with non-default charsets such as this.

  
Testing
-------

* Testing is done via the `test.py` tool, which compares the result of an encoding or decoding operation on an input file versus an expected output file. 
* Test operation: If all lines of the operation result are identical to the expected output file, the test is considered successful. Otherwise, errors are enumerated on a per-line basis, and reported to the runner.
* Test scenarios: each test scenario is specified by a JSON entry, which includes the following data:
    * test scenario alias (for printing)
    * asciiart.py arguments (e.g. `asciiart.py encode --tolerance 1`)
    * input file
    * expected output file
    * user comments (optional)
* Test results: summarized results are dumped on a per-scenario basis to stdout upon test completion. Detailed results may be written into a json file via the parameter `-r <results_file>`. Progress can be echoed to console via the `-v` (verbose) parameter.

Test tool syntax (from `python test.py -h`):

    usage: test.py [-h] [-t TESTS_FILE] [-v] [-r REPORT_FILE]

    ASCII Art test utility

    optional arguments:
      -h, --help      show this help message and exit
      -t TESTS_FILE   Test scenarios file
      -v              verbose output
      -r REPORT_FILE  Output results to report file


Charset file format
-------------------

ascii-art character sets are specified via a text file containing the following data fields:
    
    block-width
    block-height
    string-characters
    block-drawings

* `block-width`: specifies the width in characters of each ascii-art block character (included charsets use `3`).
* `block-height`: specifies the height in lines of each ascii-art block character (included charsets use `4`).
* `string-characters`: the `N` characters to be used in plaintext form (regular characters, i.e. `1234567890` for decimal digits)
* `block-drawings`: the ascii-art blocks corresponding to the above string-characters. All `block-height` lines must be exactly `block-width` characters wide. All `N` block characters must be of exact dimensions `block-width * block-height`, resulting in exactly `N * block-width * block-height` being required for this field.

All the above fields are separated by a newline character (`\n`).
