from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# --- Functions ---

def load_data():
    digits = load_digits()
    return digits.data, digits.target

def split_data(X, y):
    return train_test_split(X, y, test_size=0.3, random_state=42)

def train_model(X_train, y_train):
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))

# --- Main pipeline ---

def main():
    X, y = load_data()
    X_train, X_test, y_train, y_test = split_data(X, y)
    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)

if __name__ == "__main__":
    main()
