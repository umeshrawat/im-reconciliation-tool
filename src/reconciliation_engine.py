import pandas as pd
import os
import json
from typing import List, Dict, Tuple

class ReconciliationEngine:
    def __init__(self, trade_extract_path: str, ack_path: str, nack_path: str, error_json_path: str, ore_csv_path: str):
        self.trade_extract_path = trade_extract_path
        self.ack_path = ack_path
        self.nack_path = nack_path
        self.error_json_path = error_json_path
        self.ore_csv_path = ore_csv_path

    def reconcile(self) -> Dict[str, List[str]]:
        trade_data = self.load_trade_data()
        ack_data, nack_data = self.load_ack_nack_data()
        error_summary = self.parse_error_files()

        reconciliation_results = {
            "matched_trades": [],
            "unacknowledged_trades": [],
            "errors": error_summary
        }

        for trade in trade_data:
            if trade['TradeID'] in ack_data:
                reconciliation_results["matched_trades"].append(trade)
            elif trade['TradeID'] in nack_data:
                reconciliation_results["unacknowledged_trades"].append(trade)

        return reconciliation_results

    def load_trade_data(self) -> List[Dict[str, str]]:
        return pd.read_csv(self.trade_extract_path).to_dict(orient='records')

    def load_ack_nack_data(self) -> Tuple[List[str], List[str]]:
        ack_data = pd.read_csv(self.ack_path)['TradeID'].tolist()
        nack_data = pd.read_csv(self.nack_path)['TradeID'].tolist()
        return ack_data, nack_data

    def parse_error_files(self) -> Dict[str, List[Dict[str, str]]]:
        error_summary = {
            "transform_errors": [],
            "reconciliation_errors": []
        }

        if os.path.exists(self.error_json_path):
            with open(self.error_json_path, 'r') as f:
                transform_errors = json.load(f)
                error_summary["transform_errors"] = transform_errors.get("errors", [])

        if os.path.exists(self.ore_csv_path):
            ore_data = pd.read_csv(self.ore_csv_path).to_dict(orient='records')
            error_summary["reconciliation_errors"] = ore_data

        return error_summary