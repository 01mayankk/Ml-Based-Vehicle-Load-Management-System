import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_histogram(df, column, title, save_path):
    """Generates a histogram for a given column in a DataFrame."""
    try:
        plt.figure(figsize=(10, 6))
        sns.histplot(df[column], bins=20, kde=True)
        plt.title(title)
        plt.xlabel(column.replace('_', ' ').title())  # Format the x-axis label
        plt.ylabel("Frequency")
        plt.savefig(save_path)
        plt.close()
        logging.info(f"Histogram generated and saved to {save_path}")
        return True  # Indicate success
    except Exception as e:
        logging.error(f"Error generating histogram: {e}")
        return False  # Indicate failure

def generate_boxplot(df, column, title, save_path):
    """Generates a boxplot for a given column in a DataFrame."""
    try:
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=df[column])
        plt.title(title)
        plt.xlabel(column.replace('_', ' ').title())  # Format the x-axis label
        plt.savefig(save_path)
        plt.close()
        logging.info(f"Boxplot generated and saved to {save_path}")
        return True  # Indicate success
    except Exception as e:
        logging.error(f"Error generating boxplot: {e}")
        return False  # Indicate failure

def generate_scatter_plot(df, x_col, y_col, title, path):
    """Generates a scatter plot and saves it to a file."""
    try:
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x=x_col, y=y_col, data=df)
        plt.title(title)
        plt.xlabel(x_col.replace('_', ' ').title())
        plt.ylabel(y_col.replace('_', ' ').title())
        plt.savefig(path)
        plt.close()
        logging.info(f"Scatter plot generated and saved to {path}")
    except Exception as e:
        logging.error(f"Error generating scatter plot: {e}")

def generate_heatmap(df, title, path):
    """Generates a heatmap and saves it to a file."""
    try:
        plt.figure(figsize=(10, 8))
        sns.heatmap(df.corr(), annot=True, cmap='viridis')
        plt.title(title)
        plt.savefig(path)
        plt.close()
        logging.info(f"Heatmap generated and saved to {path}")
    except Exception as e:
        logging.error(f"Error generating heatmap: {e}")

def generate_pair_plot(df, title, save_path):
    """Generates a pair plot for a DataFrame."""
    try:
        plt.figure(figsize=(12, 10))
        sns.pairplot(df)
        plt.suptitle(title, y=1.02)  # Adjust title position
        plt.savefig(save_path)
        plt.close()
        logging.info(f"Pair plot generated and saved to {save_path}")
        return True
    except Exception as e:
        logging.error(f"Error generating pair plot: {e}")
        return False

def generate_count_plot(df, column, title, save_path):
    """Generates a count plot for a given column in a DataFrame."""
    try:
        plt.figure(figsize=(10, 6))
        sns.countplot(x=df[column])
        plt.title(title)
        plt.xlabel(column.replace('_', ' ').title())  # Format the x-axis label
        plt.ylabel("Count")
        plt.savefig(save_path)
        plt.close()
        logging.info(f"Count plot generated and saved to {save_path}")
        return True
    except Exception as e:
        logging.error(f"Error generating count plot: {e}")
        return False