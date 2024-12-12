import argparse
import json
import os

from src.parsers.parser import parse_and_fetch_structured_output_from_file_or_url
from src.utils.objectmapper import find_json_objects, merge_json_objects

def safe_open_w(path):
    """
    Open "path" for writing, creating any parent directories as needed.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'w', encoding='utf-8')




arg_parse = argparse.ArgumentParser(description='Welcome to Nutrition Parser Service !!!\n Please provide the '
                                                'file or or url which you wanna parse nutrition from.')
arg_parse.add_argument('-f', '--file', help='Enter file path or web url which you want to parse for '
                                            'nutrition info', required=True)
arg_parse.add_argument('-s', '--store', help='Enter file path where  output will be stored',
                       default='./src/outputs/restaurant_menu_nutrition_info.json')
arg_parse.add_argument('-o', '--out', help='Enter structured output format json file path',
                       default='./src/models/expected_nutrition_output_format.json')
arg_parse.add_argument('-e', '--example', help='Enter example of valid output if available',
                       default='./src/models/example_expected_valid_output.json')

args = arg_parse.parse_args()
passed_args = vars(args)

parsed_data = parse_and_fetch_structured_output_from_file_or_url(passed_args['file'],
                                                                 passed_args['out'],
                                                                 passed_args['example'])

print('parsing successful.. writing to file')

with  safe_open_w(passed_args['store']) as outfile:
    json.dump(parsed_data, outfile, indent=4)

print('parsing successful.. nutrition info written to file at: {}'.format(passed_args['store']))