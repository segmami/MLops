# CONTENU de src/data.py

import pandas as pd
from sklearn.model_selection import train_test_split
from src import config

def load_data(path=config.RAW_DATA):
    return pd.read_csv(path)                          # CSV -> DataFrame

def split_data(df):
    data = df.drop(columns=config.DROP_COLS)          # enleve id + date_naissance
    X = data.drop(columns=config.TARGET)              # features
    y = data[config.TARGET]                           # cible
    return train_test_split(X, y, test_size=config.TEST_SIZE,
                            stratify=y, random_state=config.SEED)   # split 80/20 stratifie

if __name__ == "__main__":                            # banc d'essai
    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df)
    print("Train :", X_train.shape, "| Test :", X_test.shape)
