import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize NLTK's VADER
sia = SentimentIntensityAnalyzer()

def scrape_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        article_content = ' '.join([para.get_text(strip=True) for para in paragraphs])
        
        return article_content
    except requests.RequestException as e:
        print(f"Error retrieving article from {url}: {e}")
        return ""

def analyze_sentiment_nltk(text):
    return sia.polarity_scores(text)['compound']

def analyze_sentiment_textblob(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def add_url_field():
    entry = tk.Entry(frame)
    entry.grid(row=len(url_entries), column=0, columnspan=2, pady=5, sticky='ew')
    url_entries.append(entry)

def run_analysis():
    result_text_nltk.delete('1.0', tk.END)
    result_text_textblob.delete('1.0', tk.END)
    average_sentiments = []

    for entry in url_entries:
        url = entry.get()
        if url:
            try:
                article_content = scrape_article_content(url)
                if article_content:
                    sentiment_nltk = analyze_sentiment_nltk(article_content)
                    sentiment_textblob = analyze_sentiment_textblob(article_content)
                    average_sentiments.append((sentiment_nltk + sentiment_textblob) / 2)

                    result_text_nltk.insert(tk.END, f"{url}: {sentiment_nltk}\n")
                    result_text_textblob.insert(tk.END, f"{url}: {sentiment_textblob}\n")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while processing {url}: {e}")

    if average_sentiments:
        average_sentiment = sum(average_sentiments) / len(average_sentiments)
        conclusion, color = get_conclusion(average_sentiment)
        conclusion_label.config(text=conclusion, bg=color)

def get_conclusion(average_sentiment):
    if average_sentiment > 0.1:
        return "Buy", "green"
    elif average_sentiment < -0.1:
        return "Sell", "red"
    else:
        return "Hold", "yellow"

root = tk.Tk()
root.title("Article Sentiment Analysis")

frame = tk.Frame(root)
frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

url_entries = []

add_url_button = tk.Button(frame, text="+", command=add_url_field)
add_url_button.grid(row=1, column=0, pady=5)

run_button = tk.Button(frame, text="Run Analysis", command=run_analysis)
run_button.grid(row=1, column=1, pady=5)

result_text_nltk = scrolledtext.ScrolledText(root, width=30, height=15)
result_text_nltk.grid(row=2, column=0, padx=10, pady=10)

result_text_textblob = scrolledtext.ScrolledText(root, width=30, height=15)
result_text_textblob.grid(row=2, column=1, padx=10, pady=10)

conclusion_label = tk.Label(root, text="", font=("Helvetica", 16), width=30)
conclusion_label.grid(row=3, column=0, columnspan=2, pady=10)

add_url_field()  # Add the first URL field by default

root.mainloop()
