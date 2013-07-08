asciiart
========

A python library and command-line tool to handle [ASCII-Art](http://en.wikipedia.org/wiki/ASCII_art) to Text conversions

Features
--------

* *Encoding*: convert from string to ascii-art.
* *Decoding*: convert from ascii-art to string.
* *Customizable charsets*: the user may specify a `.charset` file via the `-c` switch to select which characters will be supported. `decimal.charset` is used by default (digits 0-9), `hex.charset` is also provided (digits 0-9 and a-f, for hexadecimal base).
* *Illegal character indicators*: Whenever an invalid ascii-art character (block) is encountered, it is replaced by a special indicator (`?` by default).
* *Illegal character line indicators*: When a line with at least one illegal block is decoded, this indicator will be appended to it (` ILLEGAL` by default).
* *Block error tolerance*: Whenever an invalid ascii-art character (block) is encountered, the program can attempt to fix it buy matching it to a similar block character 'drawing'. The tolerance of the distance function is configurable by a parameter.
* *Variable line/block-line width*: The pipe can handle lines of different widths (both in plaintext and ascii-art forms). Incase a single ascii-art block-line (typically 4 lines high) varies in its line widths, an error is thrown. The last line in a ascii-art block line (typically the 4th line in the plaintext) may be empty or at the exact correct width.

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


Testing
-------




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
