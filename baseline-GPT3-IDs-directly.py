import argparse
import ast
import json
import time

from openai import OpenAI
from openai.types.chat import ChatCompletion

from evaluate import *
from file_io import *


def GPT3response(q, client: OpenAI):
    response: ChatCompletion
    messages = [{'role': 'user', 'content': q}]
    response = client.chat.completions.create(
        # curie is factor of 10 cheaper than davinci, but correspondingly less performant
        model="gpt-4",
        # model = "text-curie-001",
        messages=messages,
        temperature=0,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    response = response.choices[0].message.content
    if response[0] == " ":
        response = response[1:]
    try:
        response = ast.literal_eval(response)
    except:
        response = []
    return response


def run(args):

    client = OpenAI(api_key=args.oaikey, base_url='https://api.openai.com/v1/')

    prefix = '''State of Palestine, country-borders-country, ["Q801"]
    Paraguay, country-borders-country, ["Q155", "Q414", "Q750"]
    Lithuania, country-borders-country, ["Q34", "Q36", "Q159", "Q184", "Q211"]
    '''

    print('Starting probing GPT-3 ................')

    train_df = read_lm_kbc_jsonl_to_df(Path(args.input))

    print(train_df)

    results = []
    for idx, row in train_df.iterrows():
        prompt = prefix + row["SubjectEntity"] + ", " + row["Relation"] + ", "
        print("Prompt is \"{}\"".format(prompt))
        result = {
            "SubjectEntityID": row["SubjectEntityID"],
            "SubjectEntity": row["SubjectEntity"],
            "Relation": row["Relation"],
            "ObjectEntitiesID": GPT3response(
                prompt, client
            ),  ## naming with IDs required for current evaluation script
        }
        results.append(result)

    save_df_to_jsonl(Path(args.output), results)

    print('Finished probing GPT_3 ................')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Model with Question and Fill-Mask Prompts"
    )
    parser.add_argument(
        "-i", "--input", type=str, required=True, help="Input (subjects) file"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Predictions (output) file",
    )
    parser.add_argument(
        "-k", "--oaikey", type=str, required=True, help="OpenAI API key"
    )

    args = parser.parse_args()

    run(args)
