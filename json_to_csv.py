import json
import csv


def json_to_csv(json_file_path, csv_file_path):
    # Open the JSON file and load data
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Open the CSV file for writing
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write the header
        csv_writer.writerow(['Tactic ID', 'Tactic Name', 'Tactic Description',
                             'Technique ID', 'Technique Name', 'Technique Description',
                             'Procedure ID', 'Procedure Name', 'Procedure Description'])

        # Extract and write the data
        for tactic in data:
            tactic_id = tactic.get('id', '')
            tactic_name = tactic.get('name', '')
            tactic_description = tactic.get('description', '')

            for technique in tactic.get('techniques', []):
                technique_id = technique.get('technique_id', '')
                technique_name = technique.get('technique_name', '')
                technique_description = technique.get('technique_description', '')

                if 'procedure_examples' in technique:
                    for procedure in technique['procedure_examples']:
                        procedure_id = procedure.get('procedure_id', '')
                        procedure_name = procedure.get('procedure_name', '')
                        procedure_description = procedure.get('procedure_description', '')

                        # Write row to CSV
                        csv_writer.writerow([tactic_id, tactic_name, tactic_description,
                                             technique_id, technique_name, technique_description,
                                             procedure_id, procedure_name, procedure_description])
                else:
                    # Write row to CSV
                    csv_writer.writerow([tactic_id, tactic_name, tactic_description,
                                         technique_id, technique_name, technique_description,
                                         '', '', ''])


# Path to your JSON file
json_file_path = 'output.json'  # Replace with the path to your JSON file

# Path to your CSV file
csv_file_path = 'data.csv'  # Replace with the desired path for the CSV file

# Convert JSON to CSV
json_to_csv(json_file_path, csv_file_path)

print(f"JSON data has been successfully converted to CSV and saved to {csv_file_path}.")
