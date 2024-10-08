# -*- coding: utf-8 -*-
"""Yet another copy of Finalized_code_LLM_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zWiG-n9Z1iAwMEZ4KanK9-dsd-9JhVxp

#**Installing the Necessary Packages**
"""

pip install datasets

!pip install rouge_score evaluate

pip install transformers datasets nltk evaluate

"""#**Importing Libraries**"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
from datasets import Dataset
from transformers import GPT2Tokenizer, GPT2Config, GPT2LMHeadModel, Trainer, TrainingArguments, DataCollatorForLanguageModeling, EarlyStoppingCallback
from datasets import load_metric
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import EncoderDecoderModel, BertTokenizer

"""#**Dataset**

##Installing Kaggle API and Acquiring the arXiv Dataset
"""

# Install and configure Kaggle API
!pip install kaggle
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

# Download the dataset
!kaggle datasets download -d Cornell-University/arxiv

# Unzip the downloaded file
!unzip arxiv.zip

"""##Loading and Verifying arXiv Metadata from JSON File"""

# Load the JSON file
import json

# Open the JSON file
file_path = 'arxiv-metadata-oai-snapshot.json'
data = []

with open(file_path, 'r') as file:
    for line in file:
        data.append(json.loads(line))

# Print the first record and the length to verify
print(data[0])
print(len(data))

"""##Filtering arXiv Data for Information Retrieval Category and Creating DataFrame"""

import pandas as pd

# Filter the data
filtered_data = [paper for paper in data if 'cs.IR' in paper['categories']]

# Create a dataframe
df_ir = pd.DataFrame(filtered_data)

# Sort the dataframe by 'id'
df_ir = df_ir.sort_values(by='id').reset_index(drop=True)

# Display the dataframe
df_ir.head(20)

"""##Preprocessing and Visualizing arXiv cs.IR Paper Trends, Authors, and Keywords"""

import matplotlib.pyplot as plt
import seaborn as sns

# Convert date to datetime format
df_ir['update_date'] = pd.to_datetime(df_ir['update_date'])

# Papers over time
df_ir['year'] = df_ir['update_date'].dt.year
papers_per_year = df_ir['year'].value_counts().sort_index()

plt.figure(figsize=(12, 6))
sns.lineplot(x=papers_per_year.index, y=papers_per_year.values)
plt.title('Number of cs.IR Papers Over Time')
plt.xlabel('Year')
plt.ylabel('Number of Papers')
plt.show()

# Top authors
top_authors = df_ir['authors'].str.split(', ', expand=True).stack().value_counts().head(10)
plt.figure(figsize=(12, 6))
sns.barplot(x=top_authors.values, y=top_authors.index)
plt.title('Top 10 Authors in cs.IR Category')
plt.xlabel('Number of Papers')
plt.ylabel('Authors')
plt.show()

# Common keywords
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(stop_words='english', max_features=20)
X = vectorizer.fit_transform(df_ir['abstract'])
common_keywords = dict(zip(vectorizer.get_feature_names_out(), X.toarray().sum(axis=0)))

plt.figure(figsize=(12, 6))
sns.barplot(x=list(common_keywords.values()), y=list(common_keywords.keys()))
plt.title('Top 20 Keywords in Abstracts')
plt.xlabel('Frequency')
plt.ylabel('Keywords')
plt.show()

"""#**Preprocessing**

##Text Preprocessing for arXiv cs.IR Paper Abstracts
"""

import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize the WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

# Function to preprocess text
def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    text = text.lower()  # Lowercase the text
    words = word_tokenize(text)  # Tokenize the text into words
    words = [word for word in words if word not in stopwords.words('english')]  # Remove stop words
    words = [lemmatizer.lemmatize(word) for word in words]  # Lemmatize words
    return ' '.join(words)

# Apply the function to the 'abstract' column
df_ir['cleaned_abstract'] = df_ir['abstract'].apply(preprocess_text)

df_ir[['abstract', 'cleaned_abstract']].head(15)

df_ir.id[:20]

"""#**Data Preparation**

##Converting DataFrame to Hugging Face Dataset
"""

from datasets import Dataset
# Convert the data to a Hugging Face Dataset
dataset = Dataset.from_pandas(df_ir)

# Check the total number of samples
total_samples = len(dataset)
print(f"Total number of samples in the dataset: {total_samples}")

dataset

"""##Splitting Dataset into Training and Test Sets"""

# Split the dataset before tokenization
split_dataset = dataset.train_test_split(test_size=0.2, shuffle=False)

split_dataset

"""#**Custom Model Training**

##**Initialization and Tokenization**

###Initializing the Tokenizer
"""

# Initialize tokenizer and add a padding token
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
tokenizer.pad_token = tokenizer.eos_token

"""###Defining the Tokenization Function"""

def tokenize_function(examples):
    # Concatenate text from multiple columns
    combined_text = [
        f"{title} {cleaned_abstract} {authors} {journal_ref} {doi} {categories}"
        for title, cleaned_abstract, authors, journal_ref, doi, categories in zip(
            examples['title'], examples['cleaned_abstract'], examples['authors'],
            examples['journal-ref'], examples['doi'], examples['categories']
        )
    ]
    inputs = tokenizer(combined_text, padding='max_length', truncation=True, max_length=512)
    inputs['labels'] = inputs['input_ids'].copy()  # Make sure labels are correctly aligned
    inputs['id'] = examples['id']
    return inputs

"""###Tokenizing the Dataset"""

from datasets import Dataset, DatasetDict

# Tokenize the training set separately
tokenized_train_dataset = split_dataset['train'].map(tokenize_function, batched=True)

# Tokenize the test set separately
tokenized_test_dataset = split_dataset['test'].map(tokenize_function, batched=True)


# Combine the tokenized datasets into a DatasetDict
tokenized_datasets = DatasetDict({
    'train': tokenized_train_dataset,
    'test': tokenized_test_dataset
})

tokenized_datasets

# Verify the alignment by comparing IDs
original_train_ids = split_dataset['train']['id']
tokenized_train_ids = tokenized_datasets['train']['id']

for i in range(10):
    print(f"Original Train ID: {original_train_ids[i]}, Tokenized Train ID: {tokenized_train_ids[i]}")

# Check that the number of records matches
print(f"Number of samples in the original training set: {len(original_train_ids)}")
print(f"Number of samples in the tokenized training set: {len(tokenized_train_ids)}")

# Similarly, you can verify for the test set
original_test_ids = split_dataset['test']['id']
tokenized_test_ids = tokenized_datasets['test']['id']

for i in range(10):
    print(f"Original Test ID: {original_test_ids[i]}, Tokenized Test ID: {tokenized_test_ids[i]}")

# Verify if the IDs and texts are matching
for i in range(30):
    original_id = df_ir['id'].iloc[i]
    tokenized_id = tokenized_datasets['train'][i]['id']
    original_text = df_ir['cleaned_abstract'].iloc[i]
    tokenized_text = tokenizer.decode(tokenized_datasets['train'][i]['input_ids'],
                                      skip_special_tokens=True)

    print(f"Original ID: {original_id}, Tokenized ID: {tokenized_id}")
    print(f"Original Text:\n{original_text}\n")
    print(f"Tokenized Text:\n{tokenized_text}\n")
    print('-' * 80)

"""#**Data Collation**"""

# Initialize the data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

"""#**Custom Model Configuration**

##Defining an Argument for Custom Training
"""

# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy="epoch",
    save_strategy="epoch",  # Save checkpoints every epoch
    learning_rate=1e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=12,
    weight_decay=0.01,
    gradient_accumulation_steps=4,
    fp16=True,  # Use mixed precision training
    logging_dir='./logs',  # Directory for storing logs
    logging_steps=10,  # Log every 10 steps
    save_total_limit=2,  # Only keep the last 2 checkpoints
    load_best_model_at_end=True,  # Load the best model at the end of training
    metric_for_best_model="eval_loss",  # Metric to compare when loading the best model
)

"""##Setup the Custom Model Configuration"""

# Define the configuration with reduced parameters
config = GPT2Config(
    vocab_size=len(tokenizer),
    n_embd=1280,  # Further reduce embedding size
    n_layer=36,  # Further reduce number of layers
    n_head=32,   # Further reduce number of attention heads
    pad_token_id=tokenizer.pad_token_id,
    attn_pdrop=0.1,  # Add dropout to attention layers
    resid_pdrop=0.1,  # Add dropout to residual connections
)

"""#**Custom Model Initialization and Training**

##Initializing the Custom Model
"""

# Initialize the model with the configuration
model = GPT2LMHeadModel(config)
model.resize_token_embeddings(len(tokenizer))

# Enable gradient checkpointing
model.gradient_checkpointing_enable()

"""##Set up the Trainer"""

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['test'],
    data_collator=data_collator,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],  # Add early stopping with patience of 3 epochs
)

"""##Training the Custom Model"""

# Train the model
trainer.train()

"""#**Model Evaluation and Saving**

##Evaluating the Model
"""

import torch

# Clear cache before evaluation to free up memory
torch.cuda.empty_cache()

# Evaluate the model
results = trainer.evaluate()
print(results)

# Save the results to a dataframe for visualization
df_results = pd.DataFrame(trainer.state.log_history)
df_results.to_csv('training_log.csv', index=False)

# Plot the training and evaluation loss over epochs
if 'loss' in df_results.columns and 'eval_loss' in df_results.columns:
    plt.figure(figsize=(12, 6))
    plt.plot(df_results['epoch'], df_results['loss'], label='Training Loss')
    plt.plot(df_results['epoch'], df_results['eval_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss Over Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()
else:
    print("The DataFrame does not have the required columns for plotting.")

# Filter the DataFrame to only include rows where eval_loss is not NaN
df_filtered = df_results.dropna(subset=['eval_loss'])

# Plot the training and evaluation loss over epochs
if 'loss' in df_filtered.columns and 'eval_loss' in df_filtered.columns:
    plt.figure(figsize=(12, 6))
    plt.plot(df_filtered['epoch'], df_filtered['loss'], label='Training Loss')
    plt.plot(df_filtered['epoch'], df_filtered['eval_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss Over Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()
else:
    print("The DataFrame does not have the required columns for plotting.")

# Separate DataFrames for training and validation losses
df_training = df_results.dropna(subset=['loss'])
df_validation = df_results.dropna(subset=['eval_loss'])

plt.figure(figsize=(12, 6))
plt.plot(df_training['epoch'], df_training['loss'], label='Training Loss', color='blue')
plt.plot(df_validation['epoch'], df_validation['eval_loss'], label='Validation Loss', color='orange')
plt.title('Training and Validation Loss Over Epochs')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

file_train = pd.read_csv('training_log.csv')
file_train.head()

"""##Saving the Custom-Trained Model and Tokenizer"""

# Save the custom-trained model and tokenizer
trainer.save_model('./results')
tokenizer.save_pretrained('./results')

"""#**Loading and Testing Custom-Trained Model**

##Loading the Custom-Trained Model and Tokenizer
"""

from transformers import GPT2Tokenizer, GPT2LMHeadModel

#Load the custom-trained model and tokenizer
model = GPT2LMHeadModel.from_pretrained('./results')
tokenizer = GPT2Tokenizer.from_pretrained('./results')

"""#Defining Text Generation Function for Custom Model"""

# Function to generate text from custom
def generate_text(prompt, model, tokenizer, max_length=100):
    inputs = tokenizer.encode(prompt, return_tensors='pt',padding=True,
                              truncation=True,
                              max_length=max_length).to(model.device)
    outputs = model.generate(inputs, max_length=max_length,
                             num_return_sequences=1, no_repeat_ngram_size=2,
                             pad_token_id=tokenizer.pad_token_id)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text

def generate_text(prompt, model, tokenizer, max_length=50, num_beams=5):
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_length=max_length, num_beams=num_beams, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Example usage
generated_text = generate_text(sample_prompt, model, tokenizer)

"""##Testing Text Generation with Custom Model"""

# Test the text generation
sample_prompt_author = "An important goal for digital libraries is to enable researchers"
generated_text = generate_text(sample_prompt_author, model, tokenizer)
print(f"Generated text: {generated_text}")

# Test the text generation
sample_prompt = "The latest advancements in information retrieval"
generated_text = generate_text(sample_prompt, model, tokenizer)
print(f"Generated text: {generated_text}")

# Test the text generation
sample_prompt = "Information retrieval global effects"
generated_text = generate_text(sample_prompt, model, tokenizer)
print(f"Generated text: {generated_text}")

"""#**Loading and Testing Pre-trained BERT2BERT Model**

##Loading Pre-trained BERT2BERT Model and Tokenizer
"""

from transformers import EncoderDecoderModel, BertTokenizer

# Load pre-trained BERT2BERT model and tokenizer
pretrained_tokenizer = BertTokenizer.from_pretrained('patrickvonplaten/bert2bert_cnn_daily_mail')
pretrained_model = EncoderDecoderModel.from_pretrained('patrickvonplaten/bert2bert_cnn_daily_mail')

"""##Defining Text Generation Function for Pre-trained Model"""

# Function to generate text using pre-trained BERT2BERT model
def generate_text_pretrained(prompt, model, tokenizer, max_length=100):
    inputs = tokenizer(prompt, return_tensors='pt', padding=True,
                       truncation=True, max_length=max_length)
    input_ids = inputs.input_ids.to(model.device)
    attention_mask = inputs.attention_mask.to(model.device)

    outputs = model.generate(input_ids=input_ids, attention_mask=attention_mask,
                             max_length=max_length, num_return_sequences=1,
                             no_repeat_ngram_size=2,
                             pad_token_id=tokenizer.pad_token_id)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text

"""##Testing Text Generation with Pre-trained Model"""

sample_prompt = "The latest advancements in information retrieval"
# Generate text using pre-trained model
generated_text_pretrained = generate_text_pretrained(sample_prompt,
                                                     pretrained_model,
                                                     pretrained_tokenizer)
print(f"Generated text by pre-trained model: {generated_text_pretrained}")

sample_prompt = "Information retrieval global effects"
# Generate text using pre-trained model
generated_text_pretrained = generate_text_pretrained(sample_prompt,
                                                     pretrained_model,
                                                     pretrained_tokenizer)
print(f"Generated text by pre-trained model: {generated_text_pretrained}")

"""#**Evaluating Model Performance**

##Loading Metrics
"""

'''# Load the metrics
bleu = load_metric("bleu")
rouge = load_metric("rouge")

nltk.download('wordnet')
from nltk.translate.meteor_score import meteor_score'''

'''import evaluate
import nltk
from nltk.translate.meteor_score import meteor_score

# Load the metrics using the new evaluate library
bleu = evaluate.load("bleu")
rouge = evaluate.load("rouge")

nltk.download('wordnet')
'''

"""##Defining Function to Compute BLEU and ROUGE"""

'''# Function to compute BLEU and ROUGE
def compute_metrics(reference, generated):
    # BLEU
    bleu_score = bleu.compute(predictions=[generated.split()],
                              references=[[reference.split()]])
    print(f"BLEU score: {bleu_score['bleu']}")

    # ROUGE
    rouge_score = rouge.compute(predictions=[generated], references=[reference])
    print(f"ROUGE scores: {rouge_score}")

    # METEOR
    meteor_score_value = meteor_score([reference], generated)
    print(f"METEOR score: {meteor_score_value}")'''

"""##Computing Metrics for Generated Text"""

import evaluate
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize

# Define the reference text for comparison
reference_text = ["The latest advancements in information retrieval."]

# Text generated using pre-trained model
generated_text_pretrained = ["information retrieval is the latest advancements in information technology. information. retrievals are in the works of information - retrieval experts. more information is being. collected in data retrieval. in addition to the use of the internet, the future is on the increase. the new information processing technology is in use in digital information storage."]

# Text generated using custom-trained model
generated_text_custom = ["The latest advancements in information retrieval: a case study in this paper we present a new approach to the problem of finding the most relevant information in the information space in a given domain the goal of this approach is to identify the best practices of the data in order to be able to identify the user in an information need we have developed a method to extract the information from the documents in which the users are in their own search results are then used to find the results"]

# Load metrics using the new evaluate library
bleu = evaluate.load("bleu")
rouge = evaluate.load("rouge")

# Compute metrics for pre-trained model
print("Pre-trained model evaluation:")
bleu_score_pretrained = bleu.compute(predictions=generated_text_pretrained, references=[reference_text])
rouge_score_pretrained = rouge.compute(predictions=generated_text_pretrained, references=[reference_text])

print(f"BLEU Score: {bleu_score_pretrained['bleu']}")
print(f"ROUGE Score: {rouge_score_pretrained}")

# Compute metrics for custom-trained model
print("Custom-trained model evaluation:")
bleu_score_custom = bleu.compute(predictions=generated_text_custom, references=[reference_text])
rouge_score_custom = rouge.compute(predictions=generated_text_custom, references=[reference_text])

print(f"BLEU Score: {bleu_score_custom['bleu']}")
print(f"ROUGE Score: {rouge_score_custom}")

# Example of computing METEOR score (tokenizing first)
reference_text_tokenized = word_tokenize(reference_text[0])
generated_text_pretrained_tokenized = word_tokenize(generated_text_pretrained[0])
generated_text_custom_tokenized = word_tokenize(generated_text_custom[0])

meteor_score_pretrained = meteor_score([reference_text_tokenized], generated_text_pretrained_tokenized)
meteor_score_custom = meteor_score([reference_text_tokenized], generated_text_custom_tokenized)

print(f"METEOR Score (Pre-trained): {meteor_score_pretrained}")
print(f"METEOR Score (Custom-trained): {meteor_score_custom}")

"""##Extraction Quality Analysis"""

'''benchmark_examples = [
    {"prompt": "Recent advances in deep learning", "reference": "This paper discusses the latest advancements in deep learning and neural networks."},
    {"prompt": "Information retrieval techniques", "reference": "The study explores various information retrieval techniques and their applications."}
]

for example in benchmark_examples:
    prompt = example["prompt"]
    reference = example["reference"]
    generated = generate_text(prompt, model, tokenizer)
    print(f"Prompt: {prompt}\nGenerated: {generated}\nReference: {reference}\n")
    meteor_score_value = meteor_score([reference], generated)
    print(f"METEOR score: {meteor_score_value}\n")'''

