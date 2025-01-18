import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV files
songs_info_df = pd.read_csv('songs_info_with_ids_and_genres.csv')
overview_df = pd.read_csv('overview.csv')

# Extract track number from the 'file' column in overview_df
overview_df['Track Number'] = overview_df['file'].apply(lambda x: x.split('_')[0])

# Convert the 'Number' column in songs_info_df to string to match with 'Track Number'
songs_info_df['Number'] = songs_info_df['Number'].astype(str)

# Preprocess the Genre column
def preprocess_genre(genre):
    genre = genre.split('/')[0]  # Take the first part before any "/"
    if genre == 'Hip-Hop':
        genre = 'Hip Hop'  # Replace "Hip-Hop" with "Hip Hop"
    return genre

songs_info_df['Genre'] = songs_info_df['Genre'].apply(preprocess_genre)

# Merge the dataframes on the 'Number' and 'Track Number' columns
merged_df = pd.merge(overview_df, songs_info_df, left_on='Track Number', right_on='Number', how='left')

# Group by genre and calculate the average WER for each genre
genre_analysis = merged_df.groupby('Genre')['WER'].mean().reset_index()

# Display the result
print(genre_analysis)

# Save the genre analysis to a new CSV file
genre_analysis.to_csv('genre_analysis.csv', index=False)

# Bar Chart: Average WER by Genre
plt.figure(figsize=(10, 6))
sns.barplot(x='Genre', y='WER', data=genre_analysis)
plt.title('Average WER by Genre')
plt.xlabel('Genre')
plt.ylabel('Average WER')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('average_wer_by_genre.png')
plt.show()

# Box Plot: WER Distribution by Genre
plt.figure(figsize=(12, 8))
sns.boxplot(x='Genre', y='WER', data=merged_df)
plt.title('WER Distribution by Genre')
plt.xlabel('Genre')
plt.ylabel('WER')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('wer_distribution_by_genre.png')
plt.show()

# Scatter Plot: Tokens vs WER by Genre
plt.figure(figsize=(10, 6))
sns.scatterplot(x='tokens', y='WER', hue='Genre', data=merged_df, palette='deep')
plt.title('Tokens vs WER by Genre')
plt.xlabel('Number of Tokens')
plt.ylabel('WER')
plt.legend(title='Genre', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('tokens_vs_wer_by_genre.png')
plt.show()

# Histogram: WER Frequency Distribution by Genre
g = sns.FacetGrid(merged_df, col='Genre', col_wrap=4, height=4, aspect=1.5)
g.map(sns.histplot, 'WER', bins=20)
g.set_titles('{col_name}')
g.set_axis_labels('WER', 'Frequency')
plt.subplots_adjust(top=0.9)
g.fig.suptitle('WER Frequency Distribution by Genre')
plt.tight_layout()
g.savefig('wer_frequency_distribution_by_genre.png')
plt.show()
