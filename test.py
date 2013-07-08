#!/usr/bin/python

import json
import argparse
import StringIO
import re
from asciiart import main as run_asciiart


DEFAULT_TESTS_FILE = 'tests/scenarios.json'
DIFF_REGION_LINES_RADIUS = 2

whitespace_only_line = re.compile("^[\s]*$")


def compare_texts(out, expected, whitespace=False):
    out_lines = out.split('\n')
    exp_lines = expected.split('\n')
    results = {'equal': 0, 'diff': 0, 'whitespace': 0}
    for (lineno, (ol, el)) in enumerate(zip(out_lines, exp_lines)):
        # Equal lines
        if (ol == el):
            results['equal'] += 1
        # Ignore whitespaces (if specified by argument and both line contain only whitespaces)
        elif (not whitespace) and (whitespace_only_line.match(ol) and whitespace_only_line.match(el)):
            results['whitespace'] += 1
        # Different line content
        else:
            if results['diff'] == 0:
                results['first_diff'] = lineno
            results['diff'] += 1    

    # Include region around first diff line
    if 'first_diff' in results:
        first = results['first_diff']
        r = DIFF_REGION_LINES_RADIUS
        results['first_diff_region_out'] = out_lines[first-r:first+1+r]
        results['first_diff_region_exp'] = exp_lines[first-r:first+1+r]
    return results


def run_one_test(args_string, in_file_path, exp_out_file_path, whitespace=False):
    argv = args_string.split()
    fin = open(in_file_path, 'r')
    fout = StringIO.StringIO()   

    run_asciiart(argv, fin, fout)

    out_string = fout.getvalue()
    expected_output = open(exp_out_file_path, 'r').read()
    return compare_texts(out_string, expected_output, whitespace)


def run_tests(scenarios, verbose=0, whitespace=False):
    results = {'scenarios': {}, 'totals': {'pass': [], 'fail': []}, 'whitespace': whitespace}
    for (alias, test) in scenarios.items():
        r = run_one_test(test['args'], test['in'], test['out'], whitespace)
        success = (r['diff'] == 0)
        if success:
            results['totals']['pass'].append(alias)
            success_string = 'PASS'
        else:
            results['totals']['fail'].append(alias)
            success_string = 'FAIL'
        results['scenarios'][alias] = r
        if verbose > 0:
            print('[%s] %s' % (success_string, alias))
    if verbose > 0:
        print('')

    passed = len(results['totals']['pass'])
    failed = len(results['totals']['fail'])

    # Add count fields for convenience in output report
    results['totals']['pass_count'] = passed
    results['totals']['fail_count'] = failed

    print('passed: %d, failed: %d' % (passed, failed))
    return results


def print_report(report_file, results):
    with open(report_file, 'w') as rf:
        json.dump(results, rf, sort_keys=True, indent=4)


def parse_tests_file(file_path):
    return json.load(open(file_path, 'r'))


def main():
    parser = argparse.ArgumentParser(description='ASCII Art test utility')
    parser.add_argument('-t', default=DEFAULT_TESTS_FILE, dest='tests_file', help='test scenarios file')
    parser.add_argument('-v', action='count', dest='verbose', help='verbose output')    
    parser.add_argument('-r', default=None, dest='report_file', help='output results to report file')
    parser.add_argument('--whitespace-exact', action='store_true', dest='whitespace', help='will NOT ignore whitespace-only lines if specified')
    args = parser.parse_args()

    scenarios = parse_tests_file(args.tests_file)
    results = run_tests(scenarios, args.verbose, args.whitespace)

    if args.report_file:
        print_report(args.report_file, results)


if __name__ == "__main__":
    main()
