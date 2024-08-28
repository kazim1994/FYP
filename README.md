#  Project Title: Structure Information Extraction from Information Retrieval Research Papers Using Large Language Models

##  Project Objectives:
1.  Train and Fine-Tune a Large Language Model: The main objective is to train and fine-tune a large language model specifically     for extracting structured information from Information Retrieval (IR) research papers.
2.  Performance Comparison: Compare the performance of a custom-trained LLM with pre-trained models in extracting relevant data      from IR papers.
3.  Addressing Challenges: Identify and address potential challenges in the automated extraction process, such as handling           diverse document formats and terminologies.
##  How to Run This Notebook
To execute this notebook, follow these steps to set up your environment:
1. Set Up Hugging Face API Token:
  -  Go to Runtime > Run All.
  -  Enter HF_TOKEN as the secret name.
  -  Paste your Hugging Face API token as the value.
2. Run the Notebook Cells:
  -  Run the notebook cells as usual. Your token will be securely stored and used to authenticate API requests during the         execution.
  ##  Installation
Install the required packages by running the following command:

!pip install kaggle transformers datasets nltk evaluate rouge_score seaborn bert-score

##  Usage
###  Dataset Loading and Preprocessing
    
1.  Downloading and Unzipping the ArXiv Metadata Dataset:

  -  The ArXiv dataset is downloaded and unzipped automatically if not already present in the directory.
  -  The dataset is filtered to include only papers from the cs.IR category.
2.  Data Exploration and Analysis:

  -  Summary statistics and visualizations are generated to understand the distribution and characteristics of the dataset.
3.  Preprocessing:
  -  Text preprocessing is applied to the abstracts, including lowercasing, removing non-alphanumeric characters, and removing stop words.
  -  The cleaned text is saved in a new column cleaned_abstract in the DataFrame.
##  Model Training and Evaluation
### 1.  Custom GPT-2 Training Model
  -  A GPT-2 model is configured with custom parameters and trained from scratch on the preprocessed data.
  -  Early stopping is implemented to prevent overfitting
### 2.  Fine-Tuning a Pre-Trained GPT-2 Model:

  -  A pre-trained GPT-2 model is fine-tuned on the same dataset for comparison.
  -  Training and validation losses are plotted to evaluate model performance.
### 3.  Using a Pre-Trained BERT2BERT Model:

  -  A BERT2BERT model is utilized for text generation tasks, specifically focusing on summarization.
##  Text Generation and Evaluation
### 1.  Text Generation:

  -  Text is generated using the custom GPT-2 model, fine-tuned GPT-2 model, and pre-trained BERT2BERT model.
### 2.  Evaluation Metrics:

  -  The generated texts are evaluated using various metrics such as ROUGE, BLEU, METEOR, Distinct-N, BERTScore, and Perplexity.

##  Visualization of Results
### 1.  ROUGE Scores Comparison:

  -  The ROUGE-1 and ROUGE-L scores are compared across the models using bar charts.
### 2.  Perplexity Comparison:

  -  The perplexity of the models is calculated and plotted to assess the confidence of each model in generating text.
### 3.  BLEU, METEOR, Distinct-N, and BERTScore:

  -  Additional metrics are calculated and visualized to provide a comprehensive evaluation of the models.
##  Results
  -  The models' performances are summarized and compared using the evaluation metrics mentioned above.
  -  Visualizations such as bar charts and loss curves help to illustrate the differences in model performance.
##  License
This project is licensed under the MIT License - see the LICENSE file for details.
##  Acknowledgements
  -  Thanks to Hugging Face for providing the transformers library and pre-trained models.
  -  Special thanks to ArXiv for providing the research paper dataset used in this project.
