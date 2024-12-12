import json


BASE_PROMPT = """
you are a nutrition data parsing bot. your job is to read the provided text, images carefully and fetch the user asked data in corresponding format.
 make sure to follow strict type checks for field while parsing the data. basically you need to response with restaurant's name and list of items along with each item's nutrition information.
 Also make sure to always return result in valid JSON format where each JSON field should be enclosed in double quotes. 
"""


def build_parsing_prompt(output_structure_json_path: str, example_expected_output_json_path: str = None):
    """
    :param output_structure_json_path:
    :param example_expected_output_json_path:
    :return:
    """


    example_expected_output = None


    with open(output_structure_json_path, 'r') as f:
        output_format_data = json.load(f)


    if example_expected_output_json_path is not None:
        with open(example_expected_output_json_path, 'r') as f:
            example_expected_output = json.load(f)

    prompt = f'{BASE_PROMPT} for example if user asked you to response data in this format :- {output_format_data} \n\n\n'

    if example_expected_output is not None:
        prompt += f' \n\n for your reference, one possible valid response could be {example_expected_output}'

    return prompt
