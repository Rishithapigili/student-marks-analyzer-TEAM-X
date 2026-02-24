import pandas as pd
import matplotlib.pyplot as plt


def load_data(filepath):
    """Load the CSV file and return a DataFrame."""
    df = pd.read_csv(filepath)
    return df


def calculate_average(df):
    """Calculate and return average marks, study time, and number of courses."""
    avg_marks = df['Marks'].mean()
    avg_study_time = df['time_study'].mean()
    avg_courses = df['number_courses'].mean()
    return avg_marks, avg_study_time, avg_courses


def get_highest_scorer(df):
    """Return the row with the highest marks."""
    highest = df.loc[df['Marks'].idxmax()]
    return highest


def get_lowest_scorer(df):
    """Return the row with the lowest marks."""
    lowest = df.loc[df['Marks'].idxmin()]
    return lowest


def generate_bar_chart(df):
    """Generate a bar chart of marks per student."""
    plt.figure(figsize=(14, 6))
    plt.bar(range(1, len(df) + 1), df['Marks'], color='steelblue', edgecolor='black')
    plt.title('Student Marks - Bar Chart', fontsize=16, fontweight='bold')
    plt.xlabel('Student Index', fontsize=12)
    plt.ylabel('Marks', fontsize=12)
    plt.xticks(range(1, len(df) + 1, 5))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('bar_chart.png', dpi=150)
    plt.show()


def generate_histogram(df):
    """Generate a histogram of marks distribution."""
    plt.figure(figsize=(10, 6))
    plt.hist(df['Marks'], bins=15, color='coral', edgecolor='black', alpha=0.85)
    plt.title('Marks Distribution - Histogram', fontsize=16, fontweight='bold')
    plt.xlabel('Marks', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('histogram.png', dpi=150)
    plt.show()
