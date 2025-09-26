
python scan_git.py materialdigital --repo_name core-ontology --clone_path Test_Downloads
python extract_ontologies.py Test_Downloads --ontology_filename Test_Human.csv
python csv_to_odk.py Test_Human.csv
./script_robot.sh
