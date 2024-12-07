import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from utils.MLP import MLPSequential
from utils.preprocess import get_df, set_data_for_model_with_eval

# Create necessary directories
os.makedirs('models', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Project Introduction
st.title("MLP Classifier Interactive Application")

st.write("""
## Introduction to Multilayer Perceptron
[intro text about what is a multilayer perceptron, its components, and how it works]
""")

# Data Section
st.write("""
## Dataset Overview
[intro text about the dataset, what features it contains, and what we're trying to predict]
""")

data_path = 'data/data.csv'
df = get_df(data_path)
st.dataframe(df)

# Data Analysis Section
st.write("""
## Data Analysis
### Correlation Analysis
[intro text about correlation heatmaps and what insights we can gain from them]
""")

fig, ax = plt.subplots(figsize=(25, 20))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', linewidths=0.5, ax=ax)
ax.set_title('Feature Correlation Heatmap')
st.pyplot(fig)
plt.close()

st.write("""
### Feature Visualization
[intro text about scatter plots, how to use this section, and what patterns to look for]
""")

feature_x = st.selectbox("Select X-axis feature:", options=df.columns, index=2)
feature_y = st.selectbox("Select Y-axis feature:", options=df.columns, index=3)

fig_scatter, ax_scatter = plt.subplots()
sns.scatterplot(data=df, x=feature_x, y=feature_y, hue='diagnosis', palette='viridis', ax=ax_scatter)
ax_scatter.set_title(f'Scatter Plot: {feature_x} vs {feature_y}')
st.pyplot(fig_scatter)
plt.close()

# Model Configuration Section
st.write("""
## Evaluation Set Configuration
[intro text about the importance of having a separate evaluation set and how to choose its size]
""")

eval_size = st.slider(
    "How many subjects do you want to keep for final evaluation?", 
    min_value=1, max_value=50, value=10
)

(X_train, X_valid, X_eval, y_train, y_valid, y_eval) = set_data_for_model_with_eval(
    df, random_state=42, eval_size=eval_size
)

st.write("""
## Neural Network Architecture
[intro text about how to configure the neural network, what each parameter means, and best practices]
""")

input_size = X_train.shape[1]
model = MLPSequential(input_size)

# Interactive network configuration
num_layers = st.number_input("Number of hidden layers:", min_value=1, max_value=5, value=2)

for i in range(num_layers):
    col1, col2 = st.columns(2)
    with col1:
        neurons = st.number_input(f"Neurons in layer {i+1}:", min_value=1, max_value=100, value=24)
    with col2:
        activation = st.selectbox(
            f"Activation function for layer {i+1}:",
            options=['relu', 'sigmoid'],
            index=0
        )
    model.Dense(neurons, activation)

# Output layer configuration
output_type = st.radio(
    "Select output type:",
    options=['Binary Classification (Sigmoid)', 'Multi-class Classification (Softmax)']
)

if output_type == 'Binary Classification (Sigmoid)':
    model.Dense(1, 'sigmoid')
else:
    model.Dense(2, 'softmax')

model.compile()

# Training Configuration
st.write("""
## Model Training and Evaluation
[intro text about training parameters, what they mean, and how they affect the model]
""")

epochs = st.number_input("Enter number of epochs:", min_value=10, max_value=100000, value=1000, step=10)
learning_rate = st.number_input("Enter learning rate:", min_value=0.0001, max_value=0.1, value=0.0349, step=0.0001)
early_stopping_patience = st.slider("Early Stopping Patience:", min_value=1, max_value=50, value=5)

# Initialize session state
if 'training_completed' not in st.session_state:
    st.session_state.training_completed = False
    st.session_state.val_loss = None
    st.session_state.val_accuracy = None
    st.session_state.model = None
    st.session_state.training_results = None
    st.session_state.evaluation_results = None

if st.button("Train Model"):
    status_text = st.empty()
    progress_text = st.empty()
    
    try:
        with st.spinner('Training in progress...'):
            # Entrenar el modelo
            model.fit(X_train, y_train, epochs=epochs, learning_rate=learning_rate,
                     validation_data=(X_valid, y_valid), early_stopping_patience=early_stopping_patience)
            
            # Evaluar el modelo
            val_loss, val_accuracy = model.evaluate(X_valid, y_valid)
            
            # Guardar resultados en session_state
            st.session_state.training_completed = True
            st.session_state.val_loss = val_loss
            st.session_state.val_accuracy = val_accuracy
            st.session_state.model = model
            
            # Mostrar resultados
            st.success('Training completed!')
            st.session_state.training_results = {
                'val_loss': val_loss,
                'val_accuracy': val_accuracy
            }

            # Plots
            col1, col2 = st.columns(2)
            with col1:
                model.plot_loss()
                st.session_state.fig_loss = plt.gcf()
                st.pyplot(st.session_state.fig_loss)
            with col2:
                model.plot_accuracy()
                st.session_state.fig_acc = plt.gcf()
                st.pyplot(st.session_state.fig_acc)

            model.save_and_plot_history()
            
    except Exception as e:
        st.error(f"An error occurred during training: {str(e)}")

# Show previous training results if they exist
if st.session_state.training_results:
    st.write("### Training Results:")
    st.write(f"Validation Loss: {st.session_state.training_results['val_loss']:.4f}")
    st.write(f"Validation Accuracy: {st.session_state.training_results['val_accuracy']:.4f}")
    
    # Show plots if they exist
    if hasattr(st.session_state, 'fig_loss') and hasattr(st.session_state, 'fig_acc'):
        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(st.session_state.fig_loss)
        with col2:
            st.pyplot(st.session_state.fig_acc)

# Final Evaluation Section
if st.button("Evaluate Model"):
    if st.session_state.model is None:
        st.error("Please train the model first!")
    else:
        # Debugging information
        st.write("### Debug Information:")
        st.write("Sample of X_eval (first 5 rows):", X_eval[:5])
        st.write("Sample of y_eval (first 5 values):", y_eval[:5])
        
        y_pred = st.session_state.model.predict(X_eval)
        
        # Create DataFrame with results
        results = []
        for i, (real, pred) in enumerate(zip(y_eval, y_pred)):
            results.append({
                'Subject': i+1,
                'Real Diagnosis': 'Benign' if real == 0 else 'Malignant',
                'Predicted Diagnosis': 'Benign' if pred == 0 else 'Malignant',
                'Result': 'Success' if real == pred else 'Fail'
            })
        
        results_df = pd.DataFrame(results)
        st.write("### Evaluation Results:")
        st.dataframe(results_df)

        # Confusion Matrix
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_eval, y_pred)
        
        # Visual confusion matrix
        fig_cm, ax_cm = plt.subplots()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Benign', 'Malignant'],
                    yticklabels=['Benign', 'Malignant'], ax=ax_cm)
        ax_cm.set_xlabel('Predicted Label')
        ax_cm.set_ylabel('True Label')
        ax_cm.set_title('Confusion Matrix')
        st.pyplot(fig_cm)
        plt.close()

        # Detailed confusion matrix breakdown
        st.write("### Confusion Matrix Breakdown:")
        tn, fp, fn, tp = cm.ravel()
        st.write(f"""
        - True Negatives (Correctly identified Benign): {tn}
        - False Positives (Incorrectly identified as Malignant): {fp}
        - False Negatives (Incorrectly identified as Benign): {fn}
        - True Positives (Correctly identified Malignant): {tp}
        """)

        # Save evaluation results to session state
        st.session_state.evaluation_results = {
            'results_df': results_df,
            'confusion_matrix': cm
        }