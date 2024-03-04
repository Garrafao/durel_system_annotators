# Information on scripts in this package:

## annotate.py

The annotate.py script handles the annotation process for a given dataset. 
Here's a summarized breakdown of its functionality:

- Reads data files from a specified directory and formats them into a Pandas DataFrame.
- Calls the user-specified annotator.
- Completes the DataFrame by adding the calculated annotations and additional information.
- Writes the completed DataFrame with annotations to the output file.

### Main function
The main function forms the core of this script. It performs several tasks:
- Loads settings from a JSON file at the location specified by settings_location.
- Initializes a logging mechanism based on the debug mode status.
- Loads data files into a DataFrame.
- Specifies the XL-Lexeme annotator if it is chosen, and generates respective judgments.
- For random annotators, it generates random judgments for each instance.
- Completes the DataFrame with generated data and stores these annotations.
- Finally, saves the generated annotations to a specified path.

### Adding new Annotators
This script also allows for the easy addition of new annotators. Simply add an elif condition in the main function for the new annotator, providing the necessary settings and annotation logic for it.

### Command-line interface
Lastly, there is a command-line interface that provides options to the user to specify various aspects of the program such as which annotator to use, directories for usage and annotation data, whether to enable debug mode, thresholds for annotator, and locations for settings file.

1. Running with default settings

    `python annotate.py --usage_dir <usage_directory>`

    This will run the script with the default annotator "XL-Lexeme", default file naming and with the debug mode off. The <usage_directory> should be replaced with the actual directory path where the usage data is stored.
2. Specifying all options:
   
    ```
    python annotate.py --annotator <annotator> --prefix <prefix> --usage_dir <usage_directory> --annotation_dir <annotation_directory> --annotation_filename <annotation_filename> --debug --thresholds <thresholds> --settings_location <settings_location>
   ```
   
    Replace each argument with your actual values. In this case:
   - `annotator` could be "XL-Lexeme" or "Random".
   - `prefix` is the prefix for the usage, instance and annotation files.
   - `usage_directory` is the directory where usage data is stored.
   - `annotation_directory` is the directory where the annotations will be stored.
   - `annotation_filename` is the filename to store the annotations in.
   - --debug is an optional argument to enable debug mode.
   - `thresholds` is a list of integers to indicate thresholds for the annotator.
   - `settings_location` is the path to the settings file in JSON format.

## xl_lexeme.py

This module contains key functions to annotate a given dataset using the XL-Lexeme model. Essentially, it loads a set of sentences, calculates embeddings using XL-Lexeme word transformer, and assigns annotations based on cosine similarity of embeddings.

Key functions included are:
- `specify_xl_lexeme_annotator(thresholds: list[int])`: Specifies the type of XL-Lexeme annotator (binary, multi-threshold, or cosine) based on the length of the provided thresholds list.
- `create_annotations_for_input_data(df: pd.DataFrame, thresholds: list[float] = None, model_dir: str = None) -> list[int]`: Main function to create annotations for a given dataset. It first selects the torch device (GPU or CPU), loads the sentences from the dataset, computes embeddings using XL-Lexeme, calculates cosine similarities, and maps similarity to labels based on provided thresholds.

## status_enum.py

The status enum denotes the current status of the annotation process that can be passed on to DURel.

Possible states are: 'TASK_PENDING', 'TASK_STARTED', 'TASK_COMPLETED', 'TASK_FAILED'