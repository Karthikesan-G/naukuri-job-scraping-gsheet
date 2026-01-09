import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scraper import Output_List

def process_output(info):
    """Processing output"""
    
    try:
        df = pd.DataFrame(Output_List)

        df["SL NO."] = range(1, len(df) + 1)

        # remove dups
        df = df.drop_duplicates(subset=['NAME','COMPANY NAME','DESCRIPTION'])

        job_title_keyword = info['job_title_keyword']
        keywords = info['match_keywords']
        keywords_text = " ".join(keywords)

        documents = df['DESCRIPTION'].tolist() + [keywords_text]
        vectorizer = TfidfVectorizer(stop_words='english')

        tfidf_matrix = vectorizer.fit_transform(documents)
        cosine_similarities = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1:]) 

        percentage_matches = cosine_similarities.flatten() * 100


        #sorting percentage
        df['Match_Percentage'] = percentage_matches
        df['Match_Percentage'] = df['Match_Percentage'].astype(int)
        df = df.sort_values(by='Match_Percentage', ascending=False)
        df['Match_Percentage'] = df['Match_Percentage'].apply(lambda x: f"{x:.2f}%")

        #filterout unwanted
        if info['filter_unwanted']:
            df = df[df['Match_Percentage'] != '0.00%']
        # df = df[df['POSTED TIME'].str.contains(r'Today|Just Now|Few Hours Ago|^1 Day Ago|^2 Days Ago|^3 Days Ago|^4 Days Ago|^5 Days Ago', case=False, na=False)]

        # resetiing index values
        df.drop('SL NO.', axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.index = df.index + 1
        df.index.name = 'SL NO.'

        #filter based on location
        df = df[df['LOCATION'].str.contains(r'chennai|remote|bangalore|bangaluru|coimbatore', case=False, na=False)]

        return df

    except Exception as e:
        print(f"Error in process output function : {e}")