#!/usr/bin/python

import argparse
import sys

DEFAULT_CHARSET_FILE = 'decimal.charset'
INVALID_CHAR_INDICATOR = '?'

ADD_ILLEGAL_LINE_SUFFIX = True
ILLEGAL_LINE_SUFFIX = ' ILLEGAL'


def _block_distance(b1, b2):
    dist = 0
    for (c1, c2) in zip(b1, b2):
        if c1 != c2:
            dist += 1
    return dist


class ContentException(BaseException):
    def __init__(self, lineno=None, desc=''):
        self.lineno = lineno
        self.desc = desc

    def __str__(self):
        s = self.desc
        if not (self.lineno is None):
            s = ('[%03d] ' % (self.lineno)) + s
        return s


class AsciiArtCharset:
    def __init__(self, charset_file=DEFAULT_CHARSET_FILE, block_error_tolerance=0, block_distance_func=_block_distance, illegal_suffix=ILLEGAL_LINE_SUFFIX, invalid_char=INVALID_CHAR_INDICATOR):
        self.illegal_suffix = illegal_suffix
        self.invalid_char = invalid_char
        self.block_error_tolerance = block_error_tolerance
        self.block_distance_func = block_distance_func
        self.charmap = {}
        self.reverse_charmap = {}
        self._read_charset(charset_file)

    def _find_similar_chars(self, block):
        distances = {}
        for (ch, ch_block) in self.charmap.items():
            d = self.block_distance_func(ch_block, block)            
            if d <= self.block_error_tolerance:
                distances[ch] = d
        return sorted(distances.items(), key=lambda x: x[1])        

    def _read_charset(self, charset_file=DEFAULT_CHARSET_FILE):
        # Read the lines content
        with open(charset_file, 'r') as f:
            self.block_width = int(f.readline().strip('\r\n'))
            self.block_height = int(f.readline().strip('\r\n'))
            ascii_values = f.readline().strip('\r\n')
            expected_chars = len(ascii_values)
            drawing_lines = []
            for h in range(self.block_height):
                drawing_lines.append(f.readline().strip('\r\n'))

        # Convert to characters
        char_blocks = self._convert_one_ascii_art_line(drawing_lines)
        if len(char_blocks) != expected_chars:
            raise ContentException(desc="Invalid charset file: drawing chars count not equal to values count")
        charmap = dict(zip(ascii_values, char_blocks))

        self.charmap = charmap
        self._build_reverse_charmap()

    def _build_reverse_charmap(self):
        self.reverse_charmap = {}
        for (c, block) in self.charmap.items():
            if block in self.reverse_charmap:
                raise ContentException(desc="Invalid charset file: collision between two drawings")
            self.reverse_charmap[block] = c

    def _convert_one_ascii_art_line(self, lines): 
        if len(lines) != self.block_height:
            raise ContentException(desc="Invalid ascii art line height")
        expected_chars = None

        lines = [line.strip('\n') for line in lines]
        for (linenum, line) in enumerate(lines):            
            if (len(line) % self.block_width != 0):
                raise ContentException(linenum, "Invalid ascii art line width (%d not multiple of width %d)" % (len(line), self.block_width))
            if expected_chars is None:
                expected_chars = len(line)
            if len(line) != expected_chars:
                # allow the last line to be blanks
                if (linenum == self.block_height - 1):
                    lines[linenum] += (' ' * (expected_chars - len(lines[linenum])))
                else:
                    raise ContentException(linenum, "Invalid ascii art line: variant width (length %d chars, expected %d)" % (len(line), expected_chars))

        expected_blocks = expected_chars / self.block_width
        chars_in_line = [''] * expected_blocks
        for (linenum, line) in enumerate(lines):
            for i in range(expected_blocks):
                ind = i * self.block_width
                chars_in_line[i] += line[ind:ind+self.block_width]
        return chars_in_line

    def _print_one_block(self, block):
        ind = 0
        for h in range(self.block_height):
            print('%s' % block[ind:ind+self.block_width])
            ind += self.block_width

    def line_to_ascii_art(self, line):
        ascii_art = ''
        ind = 0
        for h in range(self.block_height):
            for c in line:
                if not c in self.charmap:
                    raise ContentException(desc="Invalid character: (ascii %d)" % ord(c))
                block = self.charmap[c]
                for w in range(self.block_width):
                    ascii_art += block[ind+w]
            ind += self.block_width
            ascii_art += '\n'
        return ascii_art

    def lines_to_ascii_art(self, lines):
        for line in lines:
            ascii_art = self.line_to_ascii_art(line)
            yield ascii_art

    def string_to_ascii_art(self, text):
        ascii_art = ''
        lines = text.split('\n')
        for line in lines:
            ascii_art += self.line_to_ascii_art(line)
        return ascii_art

    def ascii_art_line_to_string(self, lines):
        char_blocks = self._convert_one_ascii_art_line(lines)
        s = ''
        is_illegal = False
        for block in char_blocks:
            if block in self.reverse_charmap:
                s += self.reverse_charmap[block]            
            else:
                if self.block_error_tolerance > 0:
                    sc = self._find_similar_chars(block)
                    similar_chars = ''.join([ch for (ch, dist) in sc])
                    if (len(similar_chars) > 0):
                        s += similar_chars[0][0]
                    else:
                        s += self.invalid_char
                        is_illegal = True
                else:
                    s += self.invalid_char
                    is_illegal = True
        if is_illegal and self.illegal_suffix:
            s += self.illegal_suffix
        return s

    def ascii_art_to_lines(self, ascii_art_file):
        lines = []
        line_num = 0
        for line in ascii_art_file:
            line = line.strip('\n')
            lines.append(line)
            line_num += 1
            if line_num % self.block_height == 0:
                s = self.ascii_art_line_to_string(lines)
                lines = []
                yield s + '\n'


def encode_strings_to_ascii_art(string_file, ascii_art_file, charset=AsciiArtCharset()):
    for line in string_file:
        ascii_art = charset.line_to_ascii_art(line.strip('\n'))
        ascii_art_file.write(ascii_art)


def decode_ascii_art_to_strings(ascii_art_file, string_file, charset=AsciiArtCharset()):
    for line in charset.ascii_art_to_lines(ascii_art_file):
        string_file.write(line)


def test(in_path, expected_output_path, charset=AsciiArtCharset()):
    with open(in_path, 'r') as fin:
        results = [l.strip('\n') for l in charset.ascii_art_to_lines(fin)]

    with open(expected_output_path, 'r') as fexp:
        expected = [l.strip('\n') for l in fexp.readlines()]

    if len(results) > len(expected):
        raise Exception('More results than expected (%d given, %d expected)' % (len(results), len(expected)))
    else:
        good = 0
        bad = 0
        for (idx, (r, e)) in enumerate(zip(results, expected)):
            if (r != e):
                bad += 1
                print('[%03d]: "%s" vs "%s"' % (idx, r, e))
            else:
                good += 1                
    return (good, bad)


TEST_VECTORS = [
    ('input_user_story_1.txt', 'output_user_story_1.txt'),
    ('input_user_story_2.txt', 'output_user_story_2.txt'),
]


def test_all(test_vectors=TEST_VECTORS, charset=AsciiArtCharset()):
    (good, bad) = (0, 0)
    for (ipath, epath) in test_vectors:
        (g, b) = test(ipath, epath, charset)
        good += g
        bad += b
    return (good, bad)


def main(argv, fin=sys.stdin, fout=sys.stdout):
    parser = argparse.ArgumentParser(description='Text <--> ASCII Art conversion pipe (stdin --> stdout)')
    parser.add_argument('mode', choices=['encode', 'decode'], nargs=1, help='encode: ascii-art --> text, decode: text --> ascii-art')
    parser.add_argument('--charset', default=DEFAULT_CHARSET_FILE, dest='charset_path', metavar='CS', help='selects file CS as the ascii-art charset')
    parser.add_argument('--tolerance', type=int, default=0, metavar='T', dest='error_tolerance', help='conversion will tolerate errors of up to distance T')
    parser.add_argument('--no-illegal', action='store_false', dest='illegal_suffix', help='will not print the ILLEGAL suffix in-case of errors')
    parser.add_argument('--invalid_char', type=str, dest='invalid_char', metavar='C', default='?', help='will use C to indicate an unrecognized ascii-art block')
    args = parser.parse_args(argv)

    trans_mode = args.mode[0]
    tolerance = args.error_tolerance

    if args.illegal_suffix:
        illegal_suffix = ILLEGAL_LINE_SUFFIX
    else:
        illegal_suffix = None

    if len(args.invalid_char) > 1:
        raise Exception("Bad invalid character indicator given (%s)" % (args.invalid_char))

    charset = AsciiArtCharset(
        charset_file=args.charset_path, 
        block_error_tolerance=tolerance,
        illegal_suffix=illegal_suffix,
        invalid_char=args.invalid_char)

    if trans_mode == 'encode':
        encode_strings_to_ascii_art(fin, fout, charset)
    elif trans_mode == 'decode':
        decode_ascii_art_to_strings(fin, fout, charset)


if __name__ == "__main__":
    main(sys.argv[1:])
