import re
import json
import sys

def parse_complex_query(query_string):
    # Standardize the query string
    query_string = re.sub(r'\s+', ' ', query_string.strip())

    def extract_field_value(s):
        """Extract field and value from a query substring"""
        # Match for TITLE, TITLE-ABS, TITLE-ABS-KEY or AUTHKEY fields
        match = re.match(r'(TITLE-ABS-KEY|TITLE-ABS|TITLE|AUTHKEY)\("([^"]+)"\)', s.strip())
        if match:
            return {
                "field": match.group(1),
                "value": match.group(2)
            }
        return None

    def extract_srcid(s):
        """Extract SRCID values from the query string"""
        match = re.match(r'SRCID\((\d+)\)', s.strip())
        if match:
            return {
                "SRCID": match.group(1)
            }
        return None

    def parse_not_section(section):
        """Parse NOT sections"""
        # Remove outer parentheses if exists
        section = section.strip()
        if section.startswith('(') and section.endswith(')'):
            section = section[1:-1].strip()

        # Split NOT section
        if section.startswith('NOT '):
            section = section[4:].strip()  # Remove the 'NOT ' part

            # Parse the section after NOT
            parsed_section = parse_and_section(section)
            return {"NOT": parsed_section}
        return None

    def parse_or_section(section):
        """Parse OR sections"""
        # Remove outer parentheses if exists
        section = section.strip()
        if section.startswith('(') and section.endswith(')'):
            section = section[1:-1].strip()

        # Split OR sections
        or_parts = [p.strip() for p in re.split(r'\s+OR\s+', section)]

        # Extract field and value for each part
        or_results = []
        for part in or_parts:
            result = extract_field_value(part)
            if result:
                or_results.append(result)

            # Also extract SRCID if found
            srcid_result = extract_srcid(part)
            if srcid_result:
                or_results.append(srcid_result)

        # Return OR section or single result
        return {"OR": or_results} if len(or_results) > 1 else or_results[0] if or_results else None

    def parse_and_section(query):
        """Parse the entire AND-based query"""
        # Remove outer parentheses
        if query.startswith('(') and query.endswith(')'):
            query = query[1:-1].strip()

        # Split AND sections
        and_parts = [p.strip() for p in re.split(r'\s+AND\s+', query)]

        # Parse each AND section
        and_results = []
        for part in and_parts:
            # First, check for NOT sections
            not_result = parse_not_section(part)
            if not_result:
                and_results.append(not_result)
            else:
                or_result = parse_or_section(part)
                if or_result:
                    and_results.append(or_result)

        return {"AND": and_results}

    try:
        # Parse the entire query
        parsed_query = parse_and_section(query_string)
        return parsed_query
    except Exception as e:
        print(f"Error parsing query: {e}")
        return None


def process_query_file(file_path):
    try:
        with open(file_path, 'r') as f:
            query = f.read()

        # Parse the query
        parsed_result = parse_complex_query(query)

        return parsed_result
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Unexpected error reading file: {e}")
        return None


def main():
    # Check if a file path is provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "SDGQuertToJsonConverter/SDG16_2022.txt"

    # Process the query file
    query_json = process_query_file(file_path)

    # If parsing was successful, print or save the JSON
    if query_json is not None:
        # Option 1: Print to console
        print(json.dumps(query_json, indent=4))

        # Option 2: Write to JSON file
        output_file = file_path.rsplit('.', 1)[0] + '.json'
        with open(output_file, 'w') as f:
            json.dump(query_json, f, indent=4)

        print(f"\nJSON also saved to {output_file}")
    else:
        print("Failed to parse the query.")


if __name__ == "__main__":
    main()
