from pandas import read_csv
# from pandas.plotting import scatter_matrix
# from matplotlib import pyplot
from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report
# from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import warnings
from flask import current_app

def find_model(file: str):
    dataset = read_csv(file, header=0)
    current_app.logger.info(dataset.shape)
    array = dataset.values
    x = array[:, 0:3]
    y = array[:, 3]
    x_train, x_validation, y_train, y_validation = train_test_split(x, y, test_size=0.20, random_state=1)
    models = []
    models.append(('LR', LogisticRegression(solver='liblinear', multi_class='ovr')))
    models.append(('LDA', LinearDiscriminantAnalysis()))
    models.append(('KNN', KNeighborsClassifier()))
    models.append(('CART', DecisionTreeClassifier()))
    models.append(('NB', GaussianNB()))
    models.append(('SVM', SVC(gamma='auto')))
    # results = []
    # names = []
    # for name, model in models:
    #     k_fold = StratifiedKFold(n_splits=10, random_state=1, shuffle=True)
    #     cv_results = cross_val_score(model, x_train, y_train, cv=k_fold, scoring='accuracy')
    #     results.append(cv_results)
    #     names.append(name)
    #     print('%s: %f (%f)' % (name, cv_results.mean(), cv_results.std()))
    # pyplot.boxplot(results, labels=names)
    # pyplot.title('Algorithm Comparison')
    # pyplot.show()
    accuracy = 0
    chosen_model = None
    for m in models:
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                m[1].fit(x_train, y_train)
                predictions = m[1].predict(x_validation)
                if accuracy_score(y_validation, predictions) > accuracy:
                    accuracy = accuracy_score(y_validation, predictions)
                    chosen_model = m[1]
            except Warning:
                continue
    if accuracy > 0.58:
        current_app.logger.info(f"valid model found with accuracy of {accuracy}")
        return chosen_model
    else:
        current_app.logger.info(f"No model found. Closest accuracy = {accuracy}")
        return None
