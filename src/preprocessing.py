# CONTENU de src/preprocessing.py

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from src import config

def build_preprocessor():
    mean_pipe   = Pipeline([("imputer", SimpleImputer(strategy="mean"))])    # age
    median_pipe = Pipeline([("imputer", SimpleImputer(strategy="median"))])  # salaire
    cat_pipe    = Pipeline([("encoder", OneHotEncoder(handle_unknown="ignore"))])  # niveau_vie

    return ColumnTransformer([
        ("mean",   mean_pipe,     config.MEAN_IMPUTE_COLS),
        ("median", median_pipe,   config.MEDIAN_IMPUTE_COLS),
        ("cat",    cat_pipe,      config.CAT_COLS),
        ("keep",   "passthrough", config.PASSTHROUGH_COLS),
    ])

if __name__ == "__main__":
    from src.data import load_data, split_data
    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df)
    prep = build_preprocessor()
    Xp = prep.fit_transform(X_train)
    print("Shape avant :", X_train.shape, "-> apres :", Xp.shape)
