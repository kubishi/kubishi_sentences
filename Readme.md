## Reproducing Results

To reproduce the results in our paper, follow the steps below. **Note:** You must have access to the `gpt-4o` and `gpt-4o-mini` models via the OpenAI API.

### 1. Set Up Environment

Before running any scripts, create a `.env` file in the project root with your OpenAI API key:

```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 2. Install the Package

We are assuming you have downloaded the zippped repository containing this README file and extracted it to a local directory. Navigate to the root of the repository and install the package using pip:

```bash
pip install ./src
```

### 3. Enter the Scripts Directory

All reproducibility scripts are located in the `scripts` folder:

```bash
cd scripts
```


### Reproducing Only the Plots (Quick Start)

If you only want to regenerate the evaluation plots using the results already provided in the repo, simply run:

```bash
python plot_results.py
```

This will reproduce all figures shown in the paper using precomputed results stored in `yaduha/scripts/results`.


### Full Reproduction Pipeline

To reproduce the full evaluation process end-to-end (including dataset generation, fine-tuning, and evaluation), follow the steps below.

#### Step 1: Generate the Datasets

This script creates the training dataset used for fine-tuning, as described in Section 3.4 of the paper.

```bash
python generate_datasets.py
```

#### Step 2: Fine-Tune the Models

This script fine-tunes both `gpt-4o` and `gpt-4o-mini` on the generated dataset.

```bash
python finetune_models.py
```

Monitor fine-tuning job progress using OpenAI’s fine-tuning dashboard:
[https://platform.openai.com/finetune](https://platform.openai.com/finetune)

> IMPORTANT: You must update `config.py` or environment variables with the final model names once fine-tuning completes.

#### Step 3: Run Translator Evaluations

This script generates translations for all 150 evaluation sentences using each translator.

```bash
python evaluate_translators.py
```

#### Step 4: Compute Evaluation Scores

This script computes semantic similarity, BLEU, chrF++, BERTScore, and COMET scores using the translated results.

```bash
python evaluate_translators_analysis.py
```

#### Step 5: Add Manual Back-Translations

If any translators (e.g., fine-tuned or Instructions) produce ungrammatical output, you will need to manually fill in missing or invalid backwards translations in:

```
results/evaluation_results.json
```

Once complete, re-run the evaluation analysis:

```bash
python evaluate_translators_analysis.py
```


### Re-Generate Final Plots

Finally, generate the complete evaluation figures:

```bash
python plot_results.py
```

These plots will match those shown in the main paper.


Let me know if you'd like this in Markdown and LaTeX versions side-by-side.
