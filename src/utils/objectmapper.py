import regex
import json

def find_json_objects(string):
    # Regular expression to find JSON objects
    pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')

    json__string_objects = pattern.findall(string)
    json_objects = []

    for obj in json__string_objects:
       try:
           obj = json.loads(obj)
           json_objects.append(obj)
       except json.JSONDecodeError as e:
           print('error while decoding json:', e)

    return json_objects



def merge_json_objects(json_objects):
    merged = {}
    for obj in json_objects:
        for key, value in obj.items():
            if key in merged:
                if isinstance(merged[key], list) and isinstance(value, list):
                    merged[key].extend(value)  # Accumulate lists
                elif isinstance(merged[key], list):
                    merged[key].append(value)  # Append non-list value to list
                elif isinstance(value, list):
                    merged[key] = [merged[key], *value]  # Create a new list with existing and new values
                else:
                    merged[key] = [merged[key], value]  # Create a new list with existing and new values
            else:
                merged[key] = value  # Add new key-value pair

    return merged


def find_and_merge_json_objects_info_one(string: str):
    json_objects = find_json_objects(string)
    return merge_json_objects(json_objects)
