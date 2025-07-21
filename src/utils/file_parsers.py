def parse_trade_extract(file_path):
    import pandas as pd
    return pd.read_csv(file_path)

def parse_acknowledgment(file_path):
    import pandas as pd
    return pd.read_csv(file_path)

def parse_nacknowledgment(file_path):
    import pandas as pd
    return pd.read_csv(file_path)

def parse_partial_transform_failure(file_path):
    import json
    with open(file_path, 'r') as f:
        return json.load(f)

def parse_partial_ore(file_path):
    import pandas as pd
    return pd.read_csv(file_path)