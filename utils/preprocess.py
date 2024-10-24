import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import sys


def data_analysis(df):
    sns.histplot(df['radius_mean'], kde=True)
    plt.title('Distribución de Radio Medio')
    plt.show()

    sns.scatterplot(x='radius_mean', y='texture_mean', hue='diagnosis', data=df)
    plt.title('Radio Medio vs. Textura Media')
    plt.show()

    plt.figure(figsize=(20, 15))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', linewidths=0.5)
    plt.title('Matriz de Correlación de las Características')
    plt.show()

    sns.countplot(x='diagnosis', data=df)
    plt.title('Distribución de Clases (Maligno vs Benigno)')
    plt.show()

    sns.boxplot(x='diagnosis', y='radius_mean', data=df)
    plt.title('Boxplot de Radio Medio por Diagnóstico')
    plt.show()


def set_data_for_model(df, random_state):
    X = df.drop(['id', 'diagnosis'], axis=1)
    y = df['diagnosis']

    if random_state is None:
        random_state = input("Enter a random state: \n")

    if random_state == '':
        random_state = 42
    else:
        try:
            random_state = int(random_state)
        except ValueError:
            print("Please enter a valid random state.")
            sys.exit(1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test


def get_df(data_path):

    column_names = [
    'id', 'diagnosis', 'radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean', 'smoothness_mean',
    'compactness_mean', 'concavity_mean', 'concave_points_mean', 'symmetry_mean', 'fractal_dimension_mean',
    'radius_se', 'texture_se', 'perimeter_se', 'area_se', 'smoothness_se', 'compactness_se',
    'concavity_se', 'concave_points_se', 'symmetry_se', 'fractal_dimension_se',
    'radius_worst', 'texture_worst', 'perimeter_worst', 'area_worst', 'smoothness_worst',
    'compactness_worst', 'concavity_worst', 'concave_points_worst', 'symmetry_worst', 'fractal_dimension_worst'
    ]

    df = pd.read_csv(data_path, names=column_names)

    df['diagnosis'] = df['diagnosis'].map({'M': 1, 'B': 0})

    #print(df['diagnosis'].value_counts())

    #data_analysis(df)

    return df
