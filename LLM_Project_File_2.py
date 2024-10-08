# -*- coding: utf-8 -*-
"""Finalized_code_LLM_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19nwKu-JoTQnOePymRKNmdMM5kayWqWCH

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

OUTPUT

{'id': '0704.0001', 'submitter': 'Pavel Nadolsky', 'authors': "C. Bal\\'azs, E. L. Berger, P. M. Nadolsky, C.-P. Yuan", 'title': 'Calculation of prompt diphoton production cross sections at Tevatron and\n  LHC energies', 'comments': '37 pages, 15 figures; published version', 'journal-ref': 'Phys.Rev.D76:013009,2007', 'doi': '10.1103/PhysRevD.76.013009', 'report-no': 'ANL-HEP-PR-07-12', 'categories': 'hep-ph', 'license': None, 'abstract': '  A fully differential calculation in perturbative quantum chromodynamics is\npresented for the production of massive photon pairs at hadron colliders. All\nnext-to-leading order perturbative contributions from quark-antiquark,\ngluon-(anti)quark, and gluon-gluon subprocesses are included, as well as\nall-orders resummation of initial-state gluon radiation valid at\nnext-to-next-to-leading logarithmic accuracy. The region of phase space is\nspecified in which the calculation is most reliable. Good agreement is\ndemonstrated with data from the Fermilab Tevatron, and predictions are made for\nmore detailed tests with CDF and DO data. Predictions are shown for\ndistributions of diphoton pairs produced at the energy of the Large Hadron\nCollider (LHC). Distributions of the diphoton pairs from the decay of a Higgs\nboson are contrasted with those produced from QCD processes at the LHC, showing\nthat enhanced sensitivity to the signal can be obtained with judicious\nselection of events.\n', 'versions': [{'version': 'v1', 'created': 'Mon, 2 Apr 2007 19:18:42 GMT'}, {'version': 'v2', 'created': 'Tue, 24 Jul 2007 20:10:27 GMT'}], 'update_date': '2008-11-26', 'authors_parsed': [['Balázs', 'C.', ''], ['Berger', 'E. L.', ''], ['Nadolsky', 'P. M.', ''], ['Yuan', 'C. -P.', '']]}

2535068

"""##Filtering arXiv Data for Information Retrieval Category and Creating DataFrame"""

import pandas as pd

# Filter the data
filtered_data = [paper for paper in data if 'cs.IR' in paper['categories']]

# Create a dataframe
df_ir = pd.DataFrame(filtered_data)

# Display the dataframe
df_ir.head(5)


OUTPUT


id	submitter	authors	title	comments	journal-ref	doi	report-no	categories	license	abstract	versions	update_date	authors_parsed
0	0704.1158	Bernardo Huberman	Fang Wu and Bernardo A. Huberman	Novelty and Collective Attention	None	None	10.1073/pnas.0704916104	None	cs.CY cs.IR physics.soc-ph	None	The subject of collective attention is centr...	[{'version': 'v1', 'created': 'Mon, 9 Apr 2007...	2009-11-13	[[Wu, Fang, ], [Huberman, Bernardo A., ]]
1	0704.1676	Kristina Lerman	Kristina Lerman, Anon Plangprasopchok and Chio...	Personalizing Image Search Results on Flickr	12 pages, submitted to AAAI07 workshop on Inte...	None	None	None	cs.IR cs.AI cs.CY cs.DL cs.HC	None	The social media site Flickr allows users to...	[{'version': 'v1', 'created': 'Thu, 12 Apr 200...	2007-05-23	[[Lerman, Kristina, ], [Plangprasopchok, Anon,...
2	0704.2902	Stefan Pohl	Stefan Pohl, Filip Radlinski and Thorsten Joac...	Recommending Related Papers Based on Digital L...	2 pages, 3 postscript figures, to appear in pr...	None	None	None	cs.DL cs.IR	None	An important goal for digital libraries is t...	[{'version': 'v1', 'created': 'Mon, 23 Apr 200...	2007-05-23	[[Pohl, Stefan, ], [Radlinski, Filip, ], [Joac...
3	0704.2963	Stefan Pohl	Stefan Pohl	Using Access Data for Paper Recommendations on...	73 pages, 31 figures, Master's Thesis	None	None	None	cs.DL cs.IR	None	This thesis investigates in the use of acces...	[{'version': 'v1', 'created': 'Mon, 23 Apr 200...	2007-05-23	[[Pohl, Stefan, ]]
4	0704.3316	Ciro Cattuto	Ciro Cattuto, Andrea Baldassarri, Vito D. P. S...	Vocabulary growth in collaborative tagging sys...	6 pages, 7 figures	None	None	None	cs.IR cond-mat.stat-mech cs.CY physics.data-an	None	We analyze a large-scale snapshot of del.ici...	[{'version': 'v1', 'created': 'Wed, 25 Apr 200...	2007-05-23	[[Cattuto, Ciro, ], [Baldassarri, Andrea, ], [...


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
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Function to preprocess text
def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    text = text.lower()  # Lowercase the text
    return text

# Apply the function to the 'abstract' column
df_ir['cleaned_abstract'] = df_ir['abstract'].apply(preprocess_text)


# Display the dataframe
df_ir[['abstract', 'cleaned_abstract']].head()

OUTPUT

[nltk_data] Downloading package punkt to /root/nltk_data...
[nltk_data]   Unzipping tokenizers/punkt.zip.
[nltk_data] Downloading package stopwords to /root/nltk_data...
[nltk_data]   Unzipping corpora/stopwords.zip.
abstract	cleaned_abstract
0	The subject of collective attention is centr...	the subject of collective attention is centr...
1	The social media site Flickr allows users to...	the social media site flickr allows users to...
2	An important goal for digital libraries is t...	an important goal for digital libraries is t...
3	This thesis investigates in the use of acces...	this thesis investigates in the use of acces...
4	We analyze a large-scale snapshot of del.ici...	we analyze a largescale snapshot of deliciou...



"""#**Data Preparation**

##Converting DataFrame to Hugging Face Dataset
"""

from datasets import Dataset
# Convert the data to a Hugging Face Dataset
dataset = Dataset.from_pandas(df_ir)

# Check the total number of samples
total_samples = len(dataset)
print(f"Total number of samples in the dataset: {total_samples}")

OUTPUT

Total number of samples in the dataset: 17609

"""##Splitting Dataset into Training and Test Sets"""

# Split the dataset into training and evaluation sets
split_dataset = dataset.train_test_split(test_size=0.2)

# Check the number of samples in each split
train_samples = len(split_dataset['train'])
test_samples = len(split_dataset['test'])
print(f"Number of samples in the training set: {train_samples}")
print(f"Number of samples in the test set: {test_samples}")

OUTPUT

Number of samples in the training set: 14087
Number of samples in the test set: 3522

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
    return inputs

"""###Tokenizing the Dataset"""

# Map the tokenize function over the dataset
tokenized_datasets = split_dataset.map(tokenize_function, batched=True)

"""##**Data Collation**

###Initializing the Data Collator
"""

# Initialize the data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

"""##**Custom Model Configuration**

###Defining an Argument for Custom Training
"""

# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy="epoch",
    save_strategy="epoch",  # Save checkpoints every epoch
    learning_rate=3e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=15,
    weight_decay=0.01,
    gradient_accumulation_steps=4,
    fp16=True,  # Use mixed precision training
    logging_dir='./logs',  # Directory for storing logs
    logging_steps=10,  # Log every 10 steps
    save_total_limit=2,  # Only keep the last 2 checkpoints
    load_best_model_at_end=True,  # Load the best model at the end of training
    metric_for_best_model="eval_loss",  # Metric to compare when loading the best model
)

"""###Setup the Custom Model Configuration"""

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

"""##**Custom Model Initialization and Training**

###Initializing the Custom Model
"""

# Initialize the model with the configuration
model = GPT2LMHeadModel(config)
model.resize_token_embeddings(len(tokenizer))

# Enable gradient checkpointing
model.gradient_checkpointing_enable()

"""###Setting up the Trainer"""

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['test'],
    data_collator=data_collator,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],  # Add early stopping with patience of 3 epochs
)

"""###Training the Custom Model"""

# Train the model
trainer.train()


OUTPUT

`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`...
 [3300/3300 3:25:30, Epoch 14/15]
Epoch	Training Loss	Validation Loss
0	6.108200	6.071198
1	5.456100	5.371175
2	5.049600	5.028058
4	4.532900	4.613153
5	4.354600	4.447517
6	4.193700	4.345359
8	3.912100	4.208365
9	3.839500	4.175286
10	3.739600	4.140037
12	3.579300	4.102461
13	3.502200	4.096174
14	3.440800	4.096725
There were missing keys in the checkpoint model loaded: ['lm_head.weight'].
TrainOutput(global_step=3300, training_loss=4.390251329595392, metrics={'train_runtime': 12335.9387, 'train_samples_per_second': 17.129, 'train_steps_per_second': 0.268, 'total_flos': 4.593340271296512e+17, 'train_loss': 4.390251329595392, 'epoch': 14.982973893303065})

"""#**Model Evaluation and Saving**

##**Evaluating the Model**
"""

import torch

# Clear cache before evaluation to free up memory
torch.cuda.empty_cache()

# Evaluate the model
results = trainer.evaluate()
print(results)

"""##**Saving the Custom-Trained Model and Tokenizer**"""

# Save the custom-trained model and tokenizer
trainer.save_model('./results')
tokenizer.save_pretrained('./results')

OUTPUT

('./results/tokenizer_config.json',
 './results/special_tokens_map.json',
 './results/vocab.json',
 './results/merges.txt',
 './results/added_tokens.json')

"""#**Loading and Testing Custom-Trained Model**

##**Loading the Custom-Trained Model and Tokenizer**
"""

from transformers import GPT2Tokenizer, GPT2LMHeadModel

#Load the custom-trained model and tokenizer
model = GPT2LMHeadModel.from_pretrained('./results')
tokenizer = GPT2Tokenizer.from_pretrained('./results')

"""##**Defining Text Generation Function for Custom Model**"""

# Function to generate text from custom
def generate_text(prompt, model, tokenizer, max_length=100):
    inputs = tokenizer.encode(prompt, return_tensors='pt',padding=True, truncation=True, max_length=max_length).to(model.device)
    outputs = model.generate(inputs, max_length=max_length, num_return_sequences=1, no_repeat_ngram_size=2, pad_token_id=tokenizer.pad_token_id)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text

"""##**Testing Text Generation with Custom Model**"""

# Test the text generation
sample_prompt_author = "Stefan Pohl paper"
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

OUTPUT

The attention mask is not set and cannot be inferred from input because pad token is same as eos token.As a consequence, you may observe unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results.
Generated text: Stefan Pohl paper: A Novel Approach to the Web   the web is a very important problem in the internet of information retrieval
systems it is to find the most relevant information that is the user is not
important to be the information in this paper we present the concept of
information retrieval ir system which is based on the users query by using the
query in order to retrieve the query the relevant documents are relevant to
the query in a query we have used the irs based
Generated text: The latest advancements in information retrieval   in this paper we present a new approach to the problem of finding a set of
information retrieval systems in a given domain the goal is to find a user in
the user by using a search engine in order to retrieve relevant information
from a query in the user query this is a method to identify the users information in an
user query the system is based on the information need of the query and the
query in which the search system can be used to
Generated text: Information retrieval global effects in information retrieval   in this paper we present a new approach to the information filtering system in
the context of information system the system is based on the user profile of
information retrieval system and the users information systems the proposed system
is based upon the concept of the content based information and contentbased
retrieval system which is used to extract information from the query and
similar documents the results are used in the retrieval process the
experimental results show that the use of

"""#**Loading and Testing Pre-trained BERT2BERT Model**

##**Loading Pre-trained BERT2BERT Model and Tokenizer**
"""

from transformers import EncoderDecoderModel, BertTokenizer

# Load pre-trained BERT2BERT model and tokenizer
pretrained_tokenizer = BertTokenizer.from_pretrained('patrickvonplaten/bert2bert_cnn_daily_mail')
pretrained_model = EncoderDecoderModel.from_pretrained('patrickvonplaten/bert2bert_cnn_daily_mail')

"""##**Defining Text Generation Function for Pre-trained Model**"""

# Function to generate text using pre-trained BERT2BERT model
def generate_text_pretrained(prompt, model, tokenizer, max_length=100):
    inputs = tokenizer(prompt, return_tensors='pt', padding=True, truncation=True, max_length=max_length)
    input_ids = inputs.input_ids.to(model.device)
    attention_mask = inputs.attention_mask.to(model.device)

    outputs = model.generate(input_ids=input_ids, attention_mask=attention_mask, max_length=max_length, num_return_sequences=1, no_repeat_ngram_size=2, pad_token_id=tokenizer.pad_token_id)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text

"""##**Testing Text Generation with Pre-trained Model**"""

sample_prompt = "The latest advancements in information retrieval"
# Generate text using pre-trained model
generated_text_pretrained = generate_text_pretrained(sample_prompt, pretrained_model, pretrained_tokenizer)
print(f"Generated text by pre-trained model: {generated_text_pretrained}")

sample_prompt = "Information retrieval global effects"
# Generate text using pre-trained model
generated_text_pretrained = generate_text_pretrained(sample_prompt, pretrained_model, pretrained_tokenizer)
print(f"Generated text by pre-trained model: {generated_text_pretrained}")

OUTPUT

Generated text by pre-trained model: information retrieval is the latest advancements in information technology. information. retrievals are in the works of information - retrieval experts. more information is being. collected in data retrieval. in addition to the use of the internet, the future is on the increase. the new information processing technology is in use in digital information storage.
Generated text by pre-trained model: global effects of katrina are still relevant. use the daily discussion to help you understand today's featured news stories. today ’ s newsquiz includes the media literacy debate and the impact of your impact on the world effects in the aftermath of the disaster and impact impacting global impact.


"""#**Evaluating Model Performance**

##**Loading Metrics**
"""

# Load the metrics
bleu = load_metric("bleu")
rouge = load_metric("rouge")

"""##**Defining Function to Compute BLEU and ROUGE**"""

# Function to compute BLEU and ROUGE
def compute_metrics(reference, generated):
    # BLEU
    bleu_score = bleu.compute(predictions=[generated.split()], references=[[reference.split()]])
    print(f"BLEU score: {bleu_score['bleu']}")

    # ROUGE
    rouge_score = rouge.compute(predictions=[generated], references=[reference])
    print(f"ROUGE scores: {rouge_score}")

"""##**Computing Metrics for Generated Text**"""

# Define the reference text for comparison
reference_text = "The latest advancements in information retrieval."

# Text generated using pre-trained model
generated_text_pretrained = "information retrieval is the latest advancements in information technology. information. retrievals are in the works of information - retrieval experts. more information is being. collected in data retrieval. in addition to the use of the internet, the future is on the increase. the new information processing technology is in use in digital information storage."

# Text generated using custom-trained model
generated_text_custom = "The latest advancements in information retrieval: a case study in this paper we present a new approach to the problem of finding the most relevant information in the information space in a given domain the goal of this approach is to identify the best practices of the data in order to be able to identify the user in an information need we have developed a method to extract the information from the documents in which the users are in their own search results are then used to find the results"

# Compute metrics for pre-trained model
print("Pre-trained model evaluation:")
compute_metrics(reference_text, generated_text_pretrained)

# Compute metrics for custom-trained model
print("Custom-trained model evaluation:")
compute_metrics(reference_text, generated_text_custom)

OUTPUT

Pre-trained model evaluation:
BLEU score: 0.0445881574857523
ROUGE scores: {'rouge1': AggregateScore(low=Score(precision=0.11320754716981132, recall=1.0, fmeasure=0.2033898305084746), mid=Score(precision=0.11320754716981132, recall=1.0, fmeasure=0.2033898305084746), high=Score(precision=0.11320754716981132, recall=1.0, fmeasure=0.2033898305084746)), 'rouge2': AggregateScore(low=Score(precision=0.09615384615384616, recall=1.0, fmeasure=0.17543859649122806), mid=Score(precision=0.09615384615384616, recall=1.0, fmeasure=0.17543859649122806), high=Score(precision=0.09615384615384616, recall=1.0, fmeasure=0.17543859649122806)), 'rougeL': AggregateScore(low=Score(precision=0.11320754716981132, recall=1.0, fmeasure=0.2033898305084746), mid=Score(precision=0.11320754716981132, recall=1.0, fmeasure=0.2033898305084746), high=Score(precision=0.11320754716981132, recall=1.0, fmeasure=0.2033898305084746)), 'rougeLsum': AggregateScore(low=Score(precision=0.11320754716981132, recall=1.0, fmeasure=0.2033898305084746), mid=Score(precision=0.11320754716981132, recall=1.0, fmeasure=0.2033898305084746), high=Score(precision=0.11320754716981132, recall=1.0, fmeasure=0.2033898305084746))}
Custom-trained model evaluation:
BLEU score: 0.03740130030684651
ROUGE scores: {'rouge1': AggregateScore(low=Score(precision=0.06666666666666667, recall=1.0, fmeasure=0.125), mid=Score(precision=0.06666666666666667, recall=1.0, fmeasure=0.125), high=Score(precision=0.06666666666666667, recall=1.0, fmeasure=0.125)), 'rouge2': AggregateScore(low=Score(precision=0.056179775280898875, recall=1.0, fmeasure=0.10638297872340426), mid=Score(precision=0.056179775280898875, recall=1.0, fmeasure=0.10638297872340426), high=Score(precision=0.056179775280898875, recall=1.0, fmeasure=0.10638297872340426)), 'rougeL': AggregateScore(low=Score(precision=0.06666666666666667, recall=1.0, fmeasure=0.125), mid=Score(precision=0.06666666666666667, recall=1.0, fmeasure=0.125), high=Score(precision=0.06666666666666667, recall=1.0, fmeasure=0.125)), 'rougeLsum': AggregateScore(low=Score(precision=0.06666666666666667, recall=1.0, fmeasure=0.125), mid=Score(precision=0.06666666666666667, recall=1.0, fmeasure=0.125), high=Score(precision=0.06666666666666667, recall=1.0, fmeasure=0.125))}


