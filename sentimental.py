import pandas as pd

def generate_metrics_table( precision, recall, f1):
    
    data = {
        " ": ["", "micro avg", "macro avg", "weighted avg"],
        "Precision": ["", precision, precision, precision],
        "Recall": ["", recall, recall, recall],
        "F1-score": ["", f1, f1, f1]
    }

    df = pd.DataFrame(data)
    
    
    print(df.to_string(index=False))


# Example (values from your image)
generate_metrics_table( 0.92, 0.90, 0.92)