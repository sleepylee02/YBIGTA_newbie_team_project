import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_data(csv_path):
    return pd.read_csv(csv_path)

def plot_rating_distribution(data, output_dir):
    plt.figure(figsize=(8,6))
    sns.countplot(x='score', data=data)
    plt.title('Rating distribution')
    plt.xlabel('Rating')
    plt.ylabel('The count')
    plt.savefig(os.path.join(output_dir, 'rating_distribution.png'))
    plt.close()

def plot_review_length_distribution(data, output_dir):
    plt.figure(figsize=(8,6))
    sns.histplot(data['review_length'], bins=30, kde=True)
    plt.title('Review length distribution')
    plt.xlabel('Review length')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, 'review_length_distribution.png'))
    plt.close()

def plot_date_distribution(data, output_dir):
    plt.figure(figsize=(12,6))
    data['date'] = pd.to_datetime(data['date'], errors='coerce')
    data = data.dropna(subset=['date'])
    sns.histplot(data['date'], bins=30, kde=False)
    plt.title('Date distribution')
    plt.xlabel('Date')
    plt.ylabel('The count of review')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'date_distribution.png'))
    plt.close()

def main():
    csv_path = './database/reviews_kakao.csv'
    output_dir = './review_analysis/plots'
    os.makedirs(output_dir, exist_ok=True)
    
    data = load_data(csv_path)
    
    # 리뷰 길이 계산
    data['review_length'] = data['review'].astype(str).apply(len)
    
    # 분포 시각화
    plot_rating_distribution(data, output_dir)
    plot_review_length_distribution(data, output_dir)
    plot_date_distribution(data, output_dir)
    
    print("EDA 완료 및 그래프 저장됨.")

if __name__ == "__main__":
    main()
