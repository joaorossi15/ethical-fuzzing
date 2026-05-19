import pandas as pd
import os

class CanaryOutputCsv:
    columns = ["provider", "model", "seed_id", "variant_id", "canary_type", "canary_id", "canary_value", "messages", "output_text", "label", "confidence"]
    
    def __init__(self):
        self.out_df = pd.DataFrame(columns=self.columns)

    def add_to_run(self, row):
        temp = pd.DataFrame([row], columns=self.columns)
        self.out_df = pd.concat([self.out_df,temp], ignore_index=True)

    def persist(self, run_id, out_dir: str = "outputs"):
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{run_id}.csv")
        self.out_df.to_csv(path)


class ReidOutputCsv:
    columns = [
        "provider", "model", "seed_id", "variant_id",
        "case_id", "target_identity", "protected_candidates",
        "boundary_strength", "deidentification_level", "overlap_level",
        "metamorphic_relation", "probe_style",
        "deidentified_candidates",
        "deidentified_candidates_after_transformation",
        "messages", "output_text", "label", "confidence"
    ]

    def __init__(self):
        self.out_df = pd.DataFrame(columns=self.columns)

    def add_to_run(self, row):
        temp = pd.DataFrame([row], columns=self.columns)
        self.out_df = pd.concat([self.out_df, temp], ignore_index=True)

    def persist(self, run_id, out_dir: str = "outputs"):
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{run_id}.csv")
        self.out_df.to_csv(path, index=False)
        return path

