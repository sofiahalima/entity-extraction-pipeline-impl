from pathlib import Path
import json
import pandas as pd
import ast
import hashlib


def extract_entity():
    """
    extracts entity information
    the extracted_entity file adds uuid to each row, so that it can be
    merged to document dataframe for later use

    Returns:
        List  of Dict: A dictionary containing all the data from the files
    """
    project_root = Path(__file__).parent.parent
    input_dir = project_root / 'extracted_entity'
    rows = []
    for json_file in Path(input_dir).glob('*.json'):
        print("Extracting entity")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                entity_data = json.load(f)
                for item in entity_data:
                    for obj in item['entities']:
                        row = {'uuid': item['id']}
                        row.update(obj)
                        rows.append(row)
        except json.JSONDecodeError as e:
            print(f"Error reading {json_file.name}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error with {json_file.name}: {str(e)}")
        print(rows)
    return rows


def match_alias(name, label, fn_alias_df):
    """
    matches extracted entity with entity & aliases in aliases file
    when the match is found, it adds to dataframe, aliases entity_id, entity_name & marked it as matched
    using field is_matched

    Args:
        name (str): entity name from extracted entity list
        label (str): entity label from extracted entity list
        fn_alias_df (pd.DataFrame): alias dataframe

    Returns:
        returns dataframe with.
    """
    for _, row in fn_alias_df.iterrows():
        if name in row['new_aliases'] and label == row['entity_type']:
            return row['entity_id'], row['name'], 1
    return None, None, 0


def create_matched_entity_doc():
    """
    Reads document file and is merged with extracted entity

    in aliases dataframe, entity_name is added to aliases list, so that the matching can be done at once
    matched_entity_id is added  to the dataframe for normalization benefits
    matched_entity_name is added to keep track of the actual entity name
    is_matched to group matched entities

    Returns:
        returns a dataframe with  matched entity, original document data, which is to
        be later saved as csv / json / parquet for comparison purposes
        or, can be imported into database tables
    """
    project_root = Path(__file__).parent.parent
    doc_df = pd.read_csv(project_root / 'data' / 'documents.csv')
    extracted_entities = extract_entity()
    df_extracted_entities = pd.DataFrame(extracted_entities)

    df_doc_entities = pd.merge(df_extracted_entities, doc_df, on='uuid', how='inner')

    aliases_df = pd.read_csv(project_root / 'data' / 'entity_aliases.csv')
    aliases_df['entity_id'] = aliases_df.apply(
        lambda row: hashlib.sha256((row['entity_type'] + row['name']).encode()).hexdigest(), axis=1
    )

    aliases_df["aliases"] = aliases_df["aliases"].apply(ast.literal_eval)
    aliases_df["new_aliases"] = aliases_df.apply(lambda row: [row["name"]] + row["aliases"], axis=1)

    df_doc_entities[['matched_entity_id', 'matched_entity_name', 'is_matched']] = df_doc_entities.apply(
        lambda row: match_alias(row['text'], row['label'], aliases_df)
        , axis=1, result_type='expand')

    return df_doc_entities


# added for testing
if __name__ == "__main__":
    create_matched_entity_doc()
