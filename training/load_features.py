from feast import FeatureStore

FEATURE_LIST = [
    "pharmacy_features:total_sales",
    "pharmacy_features:avg_price",
    "pharmacy_features:total_quantity",
]


def load_training_features(entity_df):
    store = FeatureStore(repo_path="feature_repo")

    # Training feature retrieval
    training_df = store.get_historical_features(
        entity_df=entity_df,
        features=FEATURE_LIST,
    ).to_df()

    return training_df
